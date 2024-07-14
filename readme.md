# Python telegram bot implementation for serverless architecture

This repository contains the implementation of a Telegram bot designed to run on
a serverless architecture. 
The bot is implemented in Python and can be deployed using services such as 
AWS Lambda or yandex serverless, make file for yandex already implemented.

## Prerequisites
* Python 3.11 or higher (you can use another version, just change pyproject.toml)
* An active Telegram bot token
* [Poetry](https://python-poetry.org/) for dependency management
* [YC](https://yandex.cloud/ru/docs/cli/operations/install-cli) cli for yandex cloud deployment 


## Installation
Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-bot-serverless.git
cd telegram-bot-serverless
```

Install the dependencies (requirements file are not used, just for serverless deployment):
```bash
poetry install
```

Create a `.env` file in the root directory and add the following environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file and add your Telegram bot token:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

## Usage
To start the bot, run the following command:
```bash
python local_run.py
```

## Deployment
To deploy the bot to YC, run the following command:
```bash
chmod +x deploy-to-yc.sh
./deploy-to-yc.sh
```
Make function public in yandex cloud console or with the following command:
```bash
yc serverless function allow-unauthenticated-invoke <function_id>
```
Where `<function_id>` is the id of your lambda function from previous command. 

Then we should configure api gateway and lambda function in yandex cloud console.

And finally, we should configure webhook for our bot, for this we can use the following command:
```bash
curl -X POST "https://api.telegram.org/bot<your_telegram_bot_token>/setWebhook?url=<your_webhook_url>"
```
Where `<your_webhook_url>` is the url of your api gateway. 
And `<your_telegram_bot_token>` is token from botfather.