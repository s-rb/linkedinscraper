FROM debian:bookworm-slim

# Установите необходимые пакеты и Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    pipx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установите pipx с помощью apt
RUN apt-get install -y pipx && \
    python3 -m pipx ensurepath

# Копируем requirements.txt
COPY requirements.txt /app/requirements.txt

WORKDIR /app

# Создайте виртуальное окружение
RUN python3 -m venv /app/venv

# Активируйте виртуальное окружение и установите зависимости
RUN /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

COPY . /app

# Установите права на выполнение скриптов
RUN chmod +x main.sh

EXPOSE 5001

ENTRYPOINT ["/bin/bash", "main.sh"]