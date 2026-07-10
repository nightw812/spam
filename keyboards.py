from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

WEEKDAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="▶️ старт", callback_data="broadcast_start")
    b.button(text="⏹ стоп", callback_data="broadcast_stop")
    b.button(text="👤 аккаунт", callback_data="menu_account")
    b.button(text="👥 группы", callback_data="menu_groups")
    b.button(text="📝 контент", callback_data="menu_content")
    b.button(text="⚙️ настройка", callback_data="menu_settings")
    b.button(text="🗓 расписание рассылок", callback_data="menu_schedule")
    b.adjust(2, 2, 2, 1)
    return b.as_markup()


def back_button(target="menu_main") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ назад", callback_data=target)
    return b.as_markup()


def cancel_button() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="❌ отмена", callback_data="menu_main")
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
    b.button(text="➕ добавить аккаунт (QR)", callback_data="account_add")
    b.button(text="📱 добавить аккаунт (по коду)", callback_data="account_add_phone")
    if accounts:
        b.button(text="🚪 удалить аккаунт", callback_data="account_remove_list")
    b.button(text="⬅️ назад", callback_data="menu_main")
    b.adjust(1)
    return b.as_markup()


def account_remove_list_kb(accounts: list[dict]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for acc in accounts:
        b.button(text=f"🚪 {acc['phone']}", callback_data=f"account_remove_{acc['index']}")
    b.button(text="⬅️ назад", callback_data="menu_account")
    b.adjust(1)
    return b.as_markup()


# ---------- группы (с учётом того, что у каждого аккаунта список свой) ----------

def account_picker_kb(accounts: list[dict], prefix: str, back_cb: str) -> InlineKeyboardMarkup:
    """Список аккаунтов для выбора (используется, когда их 2 и более)."""
    b = InlineKeyboardBuilder()
    for acc in accounts:
        b.button(text=acc["phone"], callback_data=f"{prefix}_{acc['index']}")
    b.button(text="⬅️ назад", callback_data=back_cb)
    b.adjust(1)
    return b.as_markup()


def groups_menu(index: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔄 загрузить группы", callback_data=f"groups_load_{index}")
    b.button(text="☑️ выбрать группы", callback_data=f"groups_select_{index}")
    b.button(text="⬅️ назад", callback_data="menu_groups")
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

    b.button(text="☑️ все", callback_data=f"groups_all_{index}_{page}")
    b.button(text="♻️ сбросить", callback_data=f"groups_reset_{index}_{page}")
    row_sizes.append(2)

    b.button(text="⬅️ назад", callback_data=f"groups_menu_{index}")
    row_sizes.append(1)

    b.adjust(*row_sizes)
    return b.as_markup()


# ---------- контент ----------

def content_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✏️ текст", callback_data="content_set_text")
    b.button(text="🖼 фото", callback_data="content_set_photo")
    b.button(text="🖼📝 фото + текст", callback_data="content_set_photo_text")
    b.button(text="⬅️ назад", callback_data="menu_main")
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

    b.button(text="⏱ интервал", callback_data="settings_interval")
    b.button(text="🎲 пауза между отправками в группы", callback_data="settings_delay")
    row_sizes += [1, 1]

    if broadcast_count >= 2:
        b.button(text="⏳ пауза между аккаунтами", callback_data="settings_delay_between_accounts")
        row_sizes.append(1)

    b.button(text="⬅️ назад", callback_data="menu_main")
    row_sizes.append(1)

    b.adjust(*row_sizes)
    return b.as_markup()


def interval_settings_kb(index: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✏️ задать интервал", callback_data="settings_interval_set")
    b.button(text="📤 отправить один раз", callback_data="settings_interval_once")
    b.button(text="⬅️ назад", callback_data="menu_settings")
    b.adjust(1)
    return b.as_markup()


def delay_settings_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✏️ задать паузу", callback_data="settings_delay_set")
    b.button(text="⬅️ назад", callback_data="menu_settings")
    b.adjust(1)
    return b.as_markup()


def delay_between_accounts_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✏️ задать паузу", callback_data="settings_delay_between_accounts_set")
    b.button(text="⬅️ назад", callback_data="menu_settings")
    b.adjust(1)
    return b.as_markup()


# ---------- расписание ----------

def schedule_menu(entries: list[dict], enabled: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for e in entries:
        days = "каждый день" if not e["days"] else ",".join(WEEKDAY_NAMES[d] for d in e["days"])
        b.button(text=f"🗑 {e['time']} ({days})", callback_data=f"schedule_remove_{e['id']}")
    b.button(text="➕ добавить время", callback_data="schedule_add")
    b.button(text="⬅️ назад", callback_data="menu_main")
    b.adjust(1)
    return b.as_markup()


def schedule_days_kb(selected_days: list[int]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i, name in enumerate(WEEKDAY_NAMES):
        mark = "✅" if i in selected_days else "◽️"
        b.button(text=f"{mark} {name}", callback_data=f"schedule_day_{i}")
    b.button(text="📅 каждый день", callback_data="schedule_day_all")
    b.button(text="➡️ дальше (время)", callback_data="schedule_days_done")
    b.button(text="❌ отмена", callback_data="menu_schedule")
    b.adjust(4, 3, 1, 1)
    return b.as_markup()
