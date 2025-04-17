# 베이스 이미지로 Python 3.9 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 애플리케이션 코드 복사
COPY . .

# Flask와 Werkzeug 특정 버전 설치
RUN pip install --no-cache-dir flask==2.0.3 werkzeug==2.0.3

# 나머지 패키지 설치 (Flask와 Werkzeug 제외)
RUN pip install --no-cache-dir ping3==4.0.3 dnspython==2.3.0 requests==2.28.2 pyyaml>=6.0

# 포트 노출 (Flask 웹 서버용)
EXPOSE 5000

# 컨테이너 시작 시 실행할 명령어 - 웹 서버 모드로 실행
CMD ["python", "web_app.py"]
