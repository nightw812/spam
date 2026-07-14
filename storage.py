import json
import os
from threading import Lock

import config

_lock = Lock()

_DEFAULT_DELAY = {"min": config.DEFAULT_DELAY_MIN, "max": config.DEFAULT_DELAY_MAX}

_DEFAULT_ACCOUNT_EXTRA = {
    "content_type": None,
    "content_text": None,
    "content_photo": None,
    "content_forward_chat_id": None,
    "content_forward_message_id": None,
    "stat_sent": 0,
    "stat_errors": 0,
}

_DEFAULT = {
    "accounts": [],
    "broadcast_accounts": [],
    "delay_between_accounts": 0,
    "settings_account": None,
    "groups_account": None,
    "content_account": None,
    "schedule": [],
    "schedule_enabled": False,
}


# ---------- низкоуровневое хранилище пользователей ----------

def _load():
    if not os.path.exists(config.DATA_FILE):
        return {}
    with open(config.DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    os.makedirs(os.path.dirname(config.DATA_FILE), exist_ok=True)
    with open(config.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_data(user_id: int) -> dict:
    data = _load()
    stored = data.get(str(user_id), {})
    user = dict(_DEFAULT)
    user.update(stored)
    for acc in user["accounts"]:
        acc.setdefault("groups", [])
        acc.setdefault("selected", [])
        acc.setdefault("interval", None)
        acc.setdefault("delay", dict(_DEFAULT_DELAY))
        for k, v in _DEFAULT_ACCOUNT_EXTRA.items():
            acc.setdefault(k, v)
        # === ДОБАВЛЯЕМ МИГРАЦИЮ ДЛЯ INTERVAL ===
        if acc["interval"] is not None:
            # Если interval это int, преобразуем в dict
            if isinstance(acc["interval"], int):
                val = acc["interval"]
                acc["interval"] = {"min": val, "max": val}
            # Если это dict, проверяем ключи
            elif isinstance(acc["interval"], dict):
                if "min" not in acc["interval"]:
                    acc["interval"]["min"] = acc["interval"].get("max", 0)
                if "max" not in acc["interval"]:
                    acc["interval"]["max"] = acc["interval"].get("min", 0)
    # ... остальной код ...
    user.setdefault("broadcast_accounts", [])
    user.setdefault("delay_between_accounts", 0)
    user.setdefault("settings_account", None)
    user.setdefault("groups_account", None)
    user.setdefault("content_account", None)
    user.setdefault("schedule", [])
    user.setdefault("schedule_enabled", False)
    for entry in user["schedule"]:
        if "start" not in entry:
            t = entry.pop("time", "00:00")
            entry["start"] = t
            entry["end"] = t

    # авто-починка ссылок на несуществующие аккаунты
    existing = {a["index"] for a in user["accounts"]}
    user["broadcast_accounts"] = [i for i in user["broadcast_accounts"] if i in existing]
    if user["settings_account"] not in existing:
        user["settings_account"] = next(iter(existing), None)
    if user["groups_account"] not in existing:
        user["groups_account"] = next(iter(existing), None)
    if user["content_account"] not in existing:
        user["content_account"] = next(iter(existing), None)

    # Ограничиваем количество групп до MAX_GROUPS_PER_ACCOUNT
    for acc in user["accounts"]:
        if len(acc.get("groups", [])) > config.MAX_GROUPS_PER_ACCOUNT:
            acc["groups"] = acc["groups"][:config.MAX_GROUPS_PER_ACCOUNT]
        if len(acc.get("selected", [])) > config.MAX_GROUPS_PER_ACCOUNT:
            acc["selected"] = acc["selected"][:config.MAX_GROUPS_PER_ACCOUNT]

    return user


def set_user_data(user_id: int, user_data: dict):
    with _lock:
        data = _load()
        data[str(user_id)] = user_data
        _save(data)


def update_user_data(user_id: int, **fields):
    user = get_user_data(user_id)
    user.update(fields)
    set_user_data(user_id, user)
    return user


# ---------- аккаунты ----------

def next_account_index(user_id: int) -> int:
    user = get_user_data(user_id)
    used = [a["index"] for a in user["accounts"]]
    return (max(used) + 1) if used else 0


def add_account(user_id: int, index: int, phone: str):
    user = get_user_data(user_id)

    # Проверка на максимальное количество аккаунтов
    if len(user["accounts"]) >= config.MAX_ACCOUNTS_PER_USER:
        raise ValueError(f"Максимум {config.MAX_ACCOUNTS_PER_USER} аккаунтов на пользователя")

    acc = {
        "index": index,
        "phone": phone,
        "groups": [],
        "selected": [],
        "interval": None,
        "delay": dict(_DEFAULT_DELAY),
    }
    acc.update(_DEFAULT_ACCOUNT_EXTRA)
    user["accounts"].append(acc)
    if len(user["accounts"]) == 1:
        user["broadcast_accounts"] = [index]
    user["settings_account"] = index
    user["groups_account"] = index
    user["content_account"] = index
    set_user_data(user_id, user)
    register_phone(phone, user_id, index)
    return user


def remove_account(user_id: int, index: int):
    user = get_user_data(user_id)
    removed = next((a for a in user["accounts"] if a["index"] == index), None)
    user["accounts"] = [a for a in user["accounts"] if a["index"] != index]
    user["broadcast_accounts"] = [i for i in user["broadcast_accounts"] if i != index]
    if user["accounts"] and len(user["accounts"]) == 1:
        user["broadcast_accounts"] = [user["accounts"][0]["index"]]
    for field in ("settings_account", "groups_account", "content_account"):
        if user[field] == index:
            user[field] = user["accounts"][0]["index"] if user["accounts"] else None
    set_user_data(user_id, user)
    if removed:
        unregister_phone(removed["phone"])
    return user


def get_account(user_id: int, index) -> dict | None:
    if index is None:
        return None
    user = get_user_data(user_id)
    for acc in user["accounts"]:
        if acc["index"] == index:
            return acc
    return None


def update_account(user_id: int, index: int, **fields):
    user = get_user_data(user_id)
    for acc in user["accounts"]:
        if acc["index"] == index:
            acc.update(fields)
            break
    set_user_data(user_id, user)
    return user


def add_stats(user_id: int, index: int, sent: int, failed: int):
    user = get_user_data(user_id)
    for acc in user["accounts"]:
        if acc["index"] == index:
            acc["stat_sent"] = acc.get("stat_sent", 0) + sent
            acc["stat_errors"] = acc.get("stat_errors", 0) + failed
            break
    set_user_data(user_id, user)


def toggle_broadcast_account(user_id: int, index: int):
    user = get_user_data(user_id)
    if len(user["accounts"]) <= 1:
        return user
    current = set(user["broadcast_accounts"])
    if index in current:
        current.discard(index)
    else:
        current.add(index)
    user["broadcast_accounts"] = list(current)
    set_user_data(user_id, user)
    return user


def session_key(user_id: int, account_index: int) -> str:
    return f"{user_id}_{account_index}"


# ---------- реестр телефонных номеров ----------

def _load_phones():
    if not os.path.exists(config.PHONES_FILE):
        return {}
    with open(config.PHONES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_phones(data):
    os.makedirs(os.path.dirname(config.PHONES_FILE), exist_ok=True)
    with open(config.PHONES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_phone_registered(phone: str) -> bool:
    with _lock:
        return phone in _load_phones()


def register_phone(phone: str, user_id: int, account_index: int):
    with _lock:
        data = _load_phones()
        data[phone] = {"user_id": user_id, "account_index": account_index}
        _save_phones(data)


def unregister_phone(phone: str):
    with _lock:
        data = _load_phones()
        data.pop(phone, None)
        _save_phones(data)


# ---------- расписание ----------

def next_schedule_id(user_id: int) -> int:
    user = get_user_data(user_id)
    used = [e["id"] for e in user["schedule"]]
    return (max(used) + 1) if used else 0


def add_schedule_entry(user_id: int, days: list[int], start: str, end: str):
    user = get_user_data(user_id)
    entry_id = next_schedule_id(user_id)
    user["schedule"].append({"id": entry_id, "days": days, "start": start, "end": end})
    set_user_data(user_id, user)
    return user


def remove_schedule_entry(user_id: int, entry_id: int):
    user = get_user_data(user_id)
    user["schedule"] = [e for e in user["schedule"] if e["id"] != entry_id]
    set_user_data(user_id, user)
    return user


def all_user_ids_with_data() -> list[int]:
    data = _load()
    return [int(uid) for uid in data.keys()]
