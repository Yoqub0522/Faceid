# 1️⃣ Python bazasi
FROM python:3.11-slim

# 2️⃣ Ishchi papka
WORKDIR /app

# 3️⃣ Tizim kutubxonalari
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev gcc && \
    apt-get clean

# 4️⃣ Python kutubxonalarini o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4.1️⃣ Gunicorn’ni alohida o‘rnatish
RUN pip install gunicorn

# 5️⃣ Loyihani konteynerga nusxalash
COPY . .

# 6️⃣ Muhit o‘zgaruvchilari
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 7️⃣ Django port
EXPOSE 8000

# 8️⃣ Gunicorn bilan ishga tushirish
CMD ["gunicorn", "faceid_mvt.wsgi:application", "--bind", "0.0.0.0:8000"]