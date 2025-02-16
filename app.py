import threading
import subprocess

def run_scrapper():
    subprocess.run(['python3', '-u', 'scrapper.py'])

def run_ui():
    subprocess.run(['python3', '-u', 'ui.py'])

if __name__ == "__main__":
    print("Создаем потоки для запуска скраппера и UI")
    # Создаем потоки для запуска каждого файла
    ui_thread = threading.Thread(target=run_ui)
    scrapper_thread = threading.Thread(target=run_scrapper)

    print("Запускаем потоки")
    # Запускаем потоки
    ui_thread.start()
    scrapper_thread.start()

    # Ждем завершения потоков
    scrapper_thread.join()
    ui_thread.join()
    print("Все потоки завершены")