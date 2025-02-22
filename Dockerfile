FROM python:3.11-slim

# Установите необходимые пакеты и Python 3.11
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt /app/requirements.txt

WORKDIR /app

# Создайте виртуальное окружение
RUN python -m venv venv

# Активируйте виртуальное окружение и установите зависимости
RUN ./venv/bin/pip install --upgrade pip && \
    ./venv/bin/pip install -r requirements.txt

COPY . /app

# Установите права на выполнение скриптов
RUN chmod +x main.sh

EXPOSE 5001

ENTRYPOINT ["/bin/bash", "main.sh"]