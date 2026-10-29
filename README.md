# Домашняя работа по Docker

Работа анализирует текст и возвращает статистику: количество слов, символов, предложений, уникальных слов и наиболее часто встречающиеся слова.

## Быстрый запуск

Требуются Docker Desktop (или Docker Engine) и Docker Compose.

```bash
docker compose up --build -d
docker compose ps
```

**Swagger:** http://localhost:8000/docs  
**Проверка состояния:** http://localhost:8000/health

Файл `.env` создавать **необязательно**. Есть значения по умолчанию.