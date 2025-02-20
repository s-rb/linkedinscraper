import threading
import subprocess

from telegram_notifications import tg_info


def run_scrapper():
    subprocess.run(['python3', '-u', 'scrapper.py'])

def run_ui():
    subprocess.run(['python3', '-u', 'ui.py'])

if __name__ == "__main__":
    msg = "Создаем потоки для запуска скраппера и UI"
    tg_info(msg)
    # Создаем потоки для запуска каждого файла
    ui_thread = threading.Thread(target=run_ui)
    scrapper_thread = threading.Thread(target=run_scrapper)

    msg = "Запускаем потоки"
    tg_info(msg)
    # Запускаем потоки
    ui_thread.start()
    scrapper_thread.start()

    # Ждем завершения потоков
    scrapper_thread.join()
    ui_thread.join()
    msg = "Все потоки завершены"
    tg_info(msg)