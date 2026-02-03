FROM python:3.11-slim

# [필수 1] 로그가 즉시 출력되도록 설정 (Deploy 과정 확인용)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# [필수 2] Render에게 "나 8080 포트 쓸 거야"라고 알려주는 부분
EXPOSE 8080

CMD ["python", "main.py"]
