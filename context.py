import json

import redis
import tiktoken
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    EXPIRE_TIME,
    GPT_MODEL,
    EXAMPLE_REQUESTS,
    THRESHOLD,
    MESSAGES_AMOUNT,
    TOKEN_LIMIT,
    SYSTEM_PROMPT,
    MESSAGES_FOR_INFO_AMOUNT,
)

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def add_message(
    user_id: str, user_content: str, assistant_content: str, expire: bool = False
) -> None:
    """Добавление сообщения в Redis."""
    message = [
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": assistant_content},
    ]
    user_messages = redis_client.get(user_id)
    if user_messages:
        user_messages = json.loads(user_messages)
    else:
        user_messages = []
    user_messages.append(message)
    redis_client.set(user_id, json.dumps(user_messages))
    if expire:
        redis_client.expire(user_id, EXPIRE_TIME)


def get_all_messages(user_id: str) -> list:
    """Получение всех сообщений из Redis."""
    user_messages = redis_client.get(user_id)
    if user_messages:
        return json.loads(user_messages)
    return []


def count_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Подсчет количества токенов в тексте для указанной модели."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)


def combine_context_until_token_limit(
    messages: list[list[dict]], token_limit: int, new_message: str
) -> list:
    """Объединение предыдущих сообщений в контекст (до достижения предела по токенам)."""
    tokens_without_context = count_tokens(new_message) + count_tokens(SYSTEM_PROMPT)
    final_context = []
    print(messages)
    if messages:
        for message in messages:
            message_text = message[0]["content"] + message[1]["content"]
            message_tokens = count_tokens(message_text)
            final_tokens = tokens_without_context + message_tokens
            if final_tokens <= token_limit:
                final_context += message
            else:
                continue
    return final_context


def is_request_for_more_info(new_message: str) -> bool:
    """Проверка на наличие в сообщении запроса на дополнительную информацию."""
    vectorizer = TfidfVectorizer()
    x = vectorizer.fit_transform(EXAMPLE_REQUESTS)
    new_message_vector = vectorizer.transform([new_message])
    cosine_similarities = cosine_similarity(
        new_message_vector.reshape(1, -1), x
    ).flatten()
    threshold_similarity = THRESHOLD
    return any(cosine_similarities > threshold_similarity)


def get_similar_messages(
    user_id: str, new_message: str, amount: int = MESSAGES_AMOUNT
) -> list:
    """Получение похожих сообщений для формирования контекста."""
    all_messages = get_all_messages(user_id)
    all_messages_content = [
        msg[0]["content"] + msg[1]["content"] for msg in all_messages
    ] + [new_message]
    vectorizer = TfidfVectorizer().fit_transform(all_messages_content)
    vectors = vectorizer.toarray()
    if vectors.shape[0] < 2:
        return []
    cosine_sim = cosine_similarity(vectors[-1].reshape(1, -1), vectors[:-1])
    similar_indices = cosine_sim.argsort()[0][-amount:][::-1]
    return [all_messages[i] for i in similar_indices]


def generate_context(user_id: str, new_message: str, similarity: bool = True) -> list:
    """Формирование контекста для нового сообщения"""
    more_info = is_request_for_more_info(new_message)
    if more_info:
        messages = get_all_messages(user_id)[-MESSAGES_FOR_INFO_AMOUNT:]
    elif similarity:
        messages = get_similar_messages(user_id, new_message)
    else:
        messages = get_all_messages(user_id)[-MESSAGES_AMOUNT:]
    return combine_context_until_token_limit(messages, TOKEN_LIMIT, new_message)
