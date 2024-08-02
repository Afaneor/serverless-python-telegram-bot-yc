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

from config import SYSTEM_PROMPT, GPT_MODEL, TELEGRAM_BOT_TOKEN, HELP_MESSAGES
from context import generate_context, add_message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


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
    messages_context = generate_context(user_id=str(update.message.from_user.id),
                                        new_message=update.message.text)
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
                *messages_context,
                {
                    'role': 'user',
                    "content": update.message.text,
                }
            ],
            model=GPT_MODEL,
        )
        add_message(user_id=str(update.message.from_user.id),
                    user_content=update.message.text,
                    assistant_content=chat_completion.choices[0].message.content)
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
