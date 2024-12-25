FROM python:3.12.2

# для хром драйвера
RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

# директория внутри контейнера
WORKDIR /app

COPY requirements.txt /app

# установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# копируем в контейнер
COPY . /app

# порт для Flask
EXPOSE 7777

# Запускаем приложение
CMD ["python", "app.py"]
