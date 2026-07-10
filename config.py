# Токен бота от @BotFather
BOT_TOKEN = "8855863163:AAG4mJEqJOAOjdJ6nASWYycHxAce1nBL6Jo"

# api_id / api_hash с https://my.telegram.org -> API Development Tools
API_ID = 36727637
API_HASH = "383180f398a3b86e2e4143dc313a8d42"

# ID пользователей, которым разрешено пользоваться ботом.
# Это НЕ "все подряд" — доступ даёт админ вручную, вписывая сюда Telegram ID
# доверенных людей (узнать ID можно через @userinfobot).
# Каждый из них подключает СВОЙ СОБСТВЕННЫЙ аккаунт и рассылает только
# в группы, где сам состоит.
# ALLOWED_USER_IDS = {
#     8794577245,  # ты
#     8418787162,  # человек, которому доверяешь
# }

# Пауза между отправками в группы по умолчанию для НОВОГО аккаунта (секунды).
# Это диапазон "от-до" — каждая пауза выбирается случайно внутри него
# (с точностью до сотых секунды), чтобы интервалы не были одинаковыми.
DEFAULT_DELAY_MIN = 5.0
DEFAULT_DELAY_MAX = 7.0

# Как часто проверять расписание рассылок (секунды)
SCHEDULER_CHECK_INTERVAL = 20

SESSIONS_DIR = "sessions"
DATA_FILE = "data/storage.json"
PHONES_FILE = "data/phones.json"
MEDIA_DIR = "media"
