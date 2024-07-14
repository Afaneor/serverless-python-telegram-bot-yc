#!/bin/bash

# Проверка установки yc CLI
if ! command -v yc &> /dev/null
then
    echo "yc CLI не установлен. Пожалуйста, установите yc CLI и выполните настройку."
    exit 1
fi

# Запрос значений переменных окружения
read -p "Введите значение TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN
read -p "Введите значение OPENAI_API_KEY: " OPENAI_API_KEY

# Настройка переменных
FUNCTION_NAME="telegram-bot-function"
RUNTIME="python311"
ENTRYPOINT="main.handle_serverless"
TIMEOUT="10s"

# Создание функции
yc serverless function create \
  --name $FUNCTION_NAME \

# Загрузка кода функции и файла requirements.txt
zip -r function.zip main.py requirements.txt

yc serverless function version create \
  --function-name $FUNCTION_NAME \
  --runtime $RUNTIME \
  --entrypoint $ENTRYPOINT \
  --execution-timeout $TIMEOUT \
  --environment TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN",OPENAI_API_KEY="$OPENAI_API_KEY" \
  --source-path function.zip

# Удаление временного файла
rm function.zip

echo "Функция успешно развернута на Яндекс.Облако."
