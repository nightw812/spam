"""
Конфигурация. Заполни своими данными перед запуском.
"""

# Токен бота от @BotFather
BOT_TOKEN = ""

# api_id / api_hash с https://my.telegram.org -> API Development Tools
API_ID = 
API_HASH = ""

# ID пользователей, которым разрешено пользоваться ботом.
# Это НЕ "все подряд" — доступ даёт админ вручную, вписывая сюда Telegram ID
# доверенных людей (узнать ID можно через @userinfobot).
# Каждый из них подключает СВОЙ СОБСТВЕННЫЙ аккаунт и рассылает только
# в группы, где сам состоит.
ALLOWED_USER_IDS = {
    0000000000,  # ты
    0000000000,  # человек, которому доверяешь
}
ADMIN_ID = 8418787162
# Пауза между отправками в группы по умолчанию для НОВОГО аккаунта (секунды).
# Это диапазон "от-до" — каждая пауза выбирается случайно внутри него
# (с точностью до сотых секунды), чтобы интервалы не были одинаковыми.
DEFAULT_DELAY_MIN = 5.0
DEFAULT_DELAY_MAX = 7.0

# Как часто проверять расписание рассылок (секунды)
SCHEDULER_CHECK_INTERVAL = 20

# Ссылка на страницу FAQ (Telegraph). Откроется прямо в Telegram во встроенном
# просмотрщике — просто замени на свою страницу с telegra.ph.
FAQ_URL = "https://telegra.ph/SALAM"

# ID кастомных эмодзи Telegram Premium (не обязательно). Ключ — смысловое имя,
# значение — числовой emoji-id конкретного существующего Premium-эмодзи (строка).
# Как получить ID: перешли себе сообщение с нужным кастомным эмодзи в @userinfobot
# или @getmyid_bot, либо посмотри через Bot API getCustomEmojiStickers.
# Пока значение None — используется обычный текстовый emoji (см. utils/emoji.py),
# ничего не сломается, просто не будет кастомной иконки.
CUSTOM_EMOJI_IDS = {
    "start": None,
    "stop": None,
    "clock": None,
    "stats": None,
    "account": None,
    "groups": None,
    "content": None,
    "settings": None,
    "schedule": None,
    "faq": None,
    "back": None,
    "cancel": None,
    "add": None,
    "delete": None,
    "check": None,
    "cross": None,
    "circle": None,
}

SESSIONS_DIR = "sessions"
DATA_FILE = "data/storage.json"
PHONES_FILE = "data/phones.json"
STATS_FILE = "data/stats.json"
MEDIA_DIR = "media"
