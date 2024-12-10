# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем пакеты
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Устанавливаем переменную окружения для того, чтобы Python не буферизовал вывод
ENV PYTHONUNBUFFERED=1

# Открываем порт, на котором будет работать приложение
EXPOSE 8002

# Запускаем приложение
CMD ["python", "-m", "app.main"]