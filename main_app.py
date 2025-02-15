import threading
import subprocess

def run_main():
    subprocess.run(['python3', '-u', 'main.py'])

def run_app():
    subprocess.run(['python3', '-u', 'app.py'])

if __name__ == "__main__":
    print("Создаем потоки для запуска скраппера и UI")
    # Создаем потоки для запуска каждого файла
    app_thread = threading.Thread(target=run_app)
    main_thread = threading.Thread(target=run_main)

    print("Запускаем потоки")
    # Запускаем потоки
    app_thread.start()
    main_thread.start()

    # Ждем завершения потоков
    main_thread.join()
    app_thread.join()
    print("Все потоки завершены")