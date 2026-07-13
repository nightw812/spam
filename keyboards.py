from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from emoji_utils import plain, emoji_id

WEEKDAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def _btn(b: InlineKeyboardBuilder, text: str, key: str | None = None, **kwargs):
    """Добавляет кнопку. Если для key задан кастомный emoji-id в
    config.CUSTOM_EMOJI_IDS — прикрепляет его иконкой к кнопке (отдельно от
    текста, поле icon_custom_emoji_id). Пока ID не задан — просто обычная
    кнопка с обычным emoji-символом в тексте (fallback), без иконки."""
    b.button(text=text, icon_custom_emoji_id=emoji_id(key) if key else None, **kwargs)


def main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, f"{plain('start')} старт", "start", callback_data="broadcast_start")
    _btn(b, f"{plain('stop')} стоп", "stop", callback_data="broadcast_stop")
    _btn(b, f"{plain('clock')} рассылка по времени", "clock", callback_data="schedule_start")
    _btn(b, f"{plain('stats')} статистика", "stats", callback_data="menu_statistics")
    _btn(b, f"{plain('account')} аккаунт", "account", callback_data="menu_account")
    _btn(b, f"{plain('groups')} группы", "groups", callback_data="menu_groups")
    _btn(b, f"{plain('content')} контент", "content", callback_data="menu_content")
    _btn(b, f"{plain('settings')} настройка", "settings", callback_data="menu_settings")
    _btn(b, f"{plain('schedule')} расписание рассылок", "schedule", callback_data="menu_schedule")
    b.button(text=f"{plain('faq')} FAQ", icon_custom_emoji_id=emoji_id("faq"), url=config.FAQ_URL)
    b.adjust(2, 2, 2, 2, 1, 1)
    return b.as_markup()


def back_button(target="menu_main") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, f"{plain('back')} назад", "back", callback_data=target)
    return b.as_markup()


def cancel_button() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, f"{plain('cancel')} отмена", "cancel", callback_data="menu_main")
    return b.as_markup()


# ---------- аккаунты ----------

def account_menu(accounts: list[dict], broadcast_indices: list[int]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    multi = len(accounts) > 1
    for acc in accounts:
        if multi:
            mark = "✅" if acc["index"] in broadcast_indices else "◽️"
            b.button(text=f"{mark} {acc['phone']}", callback_data=f"bcacc_toggle_{acc['index']}")
        else:
            b.button(text=f"✅ {acc['phone']}", callback_data="noop")
    _btn(b, f"{plain('add')} добавить аккаунт (QR)", "add", callback_data="account_add")
    b.button(text="📱 добавить аккаунт (по коду)", callback_data="account_add_phone")
    if accounts:
        _btn(b, f"{plain('delete')} удалить аккаунт", "delete", callback_data="account_remove_list")
    _btn(b, f"{plain('back')} назад", "back", callback_data="menu_main")
    b.adjust(1)
    return b.as_markup()


def account_remove_list_kb(accounts: list[dict]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for acc in accounts:
        b.button(text=f"🚪 {acc['phone']}", callback_data=f"account_remove_{acc['index']}")
    _btn(b, f"{plain('back')} назад", "back", callback_data="menu_account")
    b.adjust(1)
    return b.as_markup()


# ---------- выбор аккаунта (используется группами и контентом, когда их 2+) ----------

def account_picker_kb(accounts: list[dict], prefix: str, back_cb: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for acc in accounts:
        b.button(text=acc["phone"], callback_data=f"{prefix}_{acc['index']}")
    _btn(b, f"{plain('back')} назад", "back", callback_data=back_cb)
    b.adjust(1)
    return b.as_markup()


# ---------- группы ----------

def groups_menu(index: int, back_target: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, "🔄 загрузить группы", "load", callback_data=f"groups_load_{index}")
    _btn(b, "☑️ выбрать группы", "select", callback_data=f"groups_select_{index}")
    _btn(b, f"{plain('back')} назад", "back", callback_data=back_target)
    b.adjust(1)
    return b.as_markup()


GROUPS_PAGE_SIZE = 20


def groups_select_kb(index: int, groups: list[dict], selected: list[int], page: int = 0) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    total_pages = max(1, (len(groups) + GROUPS_PAGE_SIZE - 1) // GROUPS_PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * GROUPS_PAGE_SIZE
    page_groups = groups[start:start + GROUPS_PAGE_SIZE]

    row_sizes = []
    for g in page_groups:
        mark = "✅" if g["id"] in selected else "◽️"
        b.button(text=f"{mark} {g['name']}", callback_data=f"toggle_{index}_{page}_{g['id']}")
        row_sizes.append(1)

    if total_pages > 1:
        nav_count = 0
        if page > 0:
            b.button(text="‹", callback_data=f"groups_page_{index}_{page - 1}")
            nav_count += 1
        b.button(text=f"{page + 1}/{total_pages}", callback_data="noop")
        nav_count += 1
        if page < total_pages - 1:
            b.button(text="›", callback_data=f"groups_page_{index}_{page + 1}")
            nav_count += 1
        row_sizes.append(nav_count)

    _btn(b, "☑️ все", "check", callback_data=f"groups_all_{index}_{page}")
    _btn(b, "♻️ сбросить", "cross", callback_data=f"groups_reset_{index}_{page}")
    row_sizes.append(2)

    _btn(b, f"{plain('back')} назад", "back", callback_data=f"groups_menu_{index}")
    row_sizes.append(1)

    b.adjust(*row_sizes)
    return b.as_markup()


# ---------- контент (на каждый аккаунт отдельно) ----------

def content_menu(index: int, back_target: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, "✏️ текст", "text", callback_data=f"content_set_text_{index}")
    _btn(b, "🖼 фото", "photo", callback_data=f"content_set_photo_{index}")
    _btn(b, "🖼📝 фото + текст", "phototext", callback_data=f"content_set_phototext_{index}")
    _btn(b, "↪️ пересылка", "forward", callback_data=f"content_set_forward_{index}")
    _btn(b, f"{plain('back')} назад", "back", callback_data=back_target)
    b.adjust(1)
    return b.as_markup()


# ---------- настройки ----------

def settings_menu(accounts: list[dict], selected_index, broadcast_count: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    row_sizes = []
    if len(accounts) > 1:
        for acc in accounts:
            mark = "🔘" if acc["index"] == selected_index else "⚪️"
            b.button(text=f"{mark} {acc['phone']}", callback_data=f"settings_switch_{acc['index']}")
        row_sizes.append(len(accounts))

    _btn(b, "⏱ интервал", "interval", callback_data="settings_interval")
    _btn(b, "🎲 пауза между отправками в группы", "pause", callback_data="settings_delay")
    row_sizes += [1, 1]

    if broadcast_count >= 2:
        _btn(b, "⏳ пауза между аккаунтами", "pause", callback_data="settings_delay_between_accounts")
        row_sizes.append(1)

    _btn(b, f"{plain('back')} назад", "back", callback_data="menu_main")
    row_sizes.append(1)

    b.adjust(*row_sizes)
    return b.as_markup()


def interval_settings_kb(index: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, "✏️ задать интервал", "interval", callback_data="settings_interval_set")
    _btn(b, "📤 отправить один раз", "once", callback_data="settings_interval_once")
    _btn(b, f"{plain('back')} назад", "back", callback_data="menu_settings")
    b.adjust(1)
    return b.as_markup()


def delay_settings_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, "✏️ задать паузу", "pause", callback_data="settings_delay_set")
    _btn(b, f"{plain('back')} назад", "back", callback_data="menu_settings")
    b.adjust(1)
    return b.as_markup()


def delay_between_accounts_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _btn(b, "✏️ задать паузу", "pause", callback_data="settings_delay_between_accounts_set")
    _btn(b, f"{plain('back')} назад", "back", callback_data="menu_settings")
    b.adjust(1)
    return b.as_markup()


# ---------- расписание (окна времени: начало-конец) ----------

def schedule_menu(entries: list[dict], enabled: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for e in entries:
        days = "каждый день" if not e["days"] else ",".join(WEEKDAY_NAMES[d] for d in e["days"])
        b.button(
            text=f"🗑 {e['start']}–{e['end']} ({days})",
            callback_data=f"schedule_remove_{e['id']}",
        )
    _btn(b, f"{plain('add')} добавить время", "add", callback_data="schedule_add")
    _btn(b, f"{plain('back')} назад", "back", callback_data="menu_main")
    b.adjust(1)
    return b.as_markup()


def schedule_days_kb(selected_days: list[int]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i, name in enumerate(WEEKDAY_NAMES):
        mark = "✅" if i in selected_days else "◽️"
        b.button(text=f"{mark} {name}", callback_data=f"schedule_day_{i}")
    b.button(text="📅 каждый день", callback_data="schedule_day_all")
    b.button(text="➡️ дальше (время)", callback_data="schedule_days_done")
    _btn(b, f"{plain('cancel')} отмена", "cancel", callback_data="menu_schedule")
    b.adjust(4, 3, 1, 1)
    return b.as_markup()
