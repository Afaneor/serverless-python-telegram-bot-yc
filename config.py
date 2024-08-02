from decouple import config


SYSTEM_PROMPT = """
Ты являешься ботом телеграмм канала "Павлин Шарит", ты должен помогать
подписчикам помогать технические ворпосы, твоя задача давать подробный и 
развернутый ответ и объяснять почему ты считаешь именно так. Ответы должны 
содержать максимально оптимизированные решения, потому что подписчики 
заслуживают качественно и экспертной помощи. По возможности приводи ссылки, где
можно прочитать про это подробнее 
"""
ALLOWED_CHATS = []
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
HELP_MESSAGES = ('gpt', )
GPT_MODEL = config('GPT_MODEL', 'gpt-3.5-turbo')

EXPIRE_TIME = 300

TOKEN_LIMIT = 4096
EXAMPLE_REQUESTS = [
    "Расскажи подробнее.",
    "Можешь объяснить это?",
    "Дай развёрнутый ответ.",
    "Ещё раз, пожалуйста.",
    "Опиши это подробнее.",
]
THRESHOLD = 0.1
MESSAGES_AMOUNT = 5
MESSAGES_FOR_INFO_AMOUNT = 1

REDIS_DB = config('REDIS_DB', default=0)
REDIS_HOST = config('REDIS_HOST', default="localhost")
REDIS_PORT = config('REDIS_PORT', default=6379)
