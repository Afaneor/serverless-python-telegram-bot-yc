import json
from typing import List

from openai import OpenAI
from telegram import Update, Message
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from functools import wraps
from decouple import config
from chatgpt_md_converter import telegram_format

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


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


class TextStartsWithFilter(filters.Text):

    def filter(self, message: Message) -> bool:
        """Проверка наличия текста в сообщении."""
        return bool(message.text and any(
            message.text.startswith(string) for string in self.strings
        ))


def allow_chats(chats: List[int] | None = None):
    """Декоратор обрабатывающий сообщения только из определнных чатов."""
    def inner(func):
        @wraps(func)
        async def wrapped(
                update: Update,
                context: ContextTypes.DEFAULT_TYPE,
                *args,
                **kwargs,
        ):
            chat = update.effective_chat.id
            if chats is not None and chat not in chats:
                logger.info(f'Chat {chat} is not allowed')
                return
            return await func(update, context, *args, **kwargs)
        return wrapped
    return inner


@allow_chats()
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик, который отвечает на сообщение."""
    # TODO пробрасывать контекст всех ответов по ветке сообщений
    client = OpenAI(
        api_key=config("OPENAI_API_KEY"),
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    'role': 'system',
                    "content": SYSTEM_PROMPT,
                },
                {
                    'role': 'user',
                    "content": update.message.text,
                }
            ],
            model=GPT_MODEL,
        )
    except Exception as e:
        logger.error(f'Error while getting completion: {e}')
        await update.message.reply_text('Возникла ошибка, попробуйте позднее')
        return
    answer = telegram_format(chat_completion.choices[0].message.content)
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=answer,
        reply_to_message_id=update.message.id,
        parse_mode='html',
    )


app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).write_timeout(15).build()
app.add_handler(MessageHandler(TextStartsWithFilter(HELP_MESSAGES), gpt))


async def handle_serverless(event, context):
    """Обработка событий serverless."""
    await app.initialize()
    logger.info(f'Event: {event}')
    try:
        await app.process_update(Update.de_json(json.loads(event['body'])))
    except Exception as e:
        logger.error(f'Error while processing update: {e}')
        return {'statusCode': 500}

    return {'statusCode': 200}
