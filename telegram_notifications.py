import requests
import json

def load_config(file_name):
    # Load the config file
    with open(file_name) as f:
        return json.load(f)

config = load_config('config.json')
TELEGRAM_BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = config["TELEGRAM_CHAT_ID"]


def send_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Используйте Markdown для форматирования
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")

def tg_info(message):
    try:
        msg = f"ℹ️ Информация: {message}"
        print(msg)
        send_message(msg)
    except Exception as ex:
        print(f"Произошла ошибка при отправке в Телеграм сообщения: {message}", ex)

def tg_error(message, exception=None):
    try:
        error_message = f"❌ Ошибка: {message}\n`{str(exception)}`" if exception is not None else f"❌ Ошибка: {message}"
        send_message(error_message)
    except Exception as ex:
        exc = f"\n{exception}" if exception is not None else ''
        print(f"Произошла ошибка при отправке в Телеграм сообщения: {message}{exc}", ex)