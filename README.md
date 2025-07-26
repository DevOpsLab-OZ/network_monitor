# 네트워크 모니터링 도구

Python을 사용한 종합적인 네트워크 모니터링 도구입니다. 

기본적인 네트워크 진단 기능과 모니터링 기능을 제공하여 네트워크 상태를 파악하고 문제를 진단하는 데 도움을 줍니다.

## 현재 구현된 기능

### feature/ping
- **기본 프로젝트 구조 설정**
- **Ping 테스트 기능**:
  - 특정 호스트의 응답 시간 측정
  - 패킷 손실률 계산
  - 최소/최대/평균 응답 시간 통계

### feature/scan
- **포트 스캔 기능**:
  - 특정 호스트의 열린 포트 확인
  - 서비스 이름 식별
  - 커스텀 포트 범위 지정 가능
  - 일반적인 포트만 스캔하는 옵션
  - 멀티스레딩을 이용한 병렬 스캔

### feature/dns
- **DNS 조회 기능**:
  - 도메인 이름에 대한 다양한 DNS 레코드 조회 (A, AAAA, MX, NS, TXT, SOA, CNAME)
  - IP 주소에 대한 역방향 DNS 조회
  - 상세한 DNS 정보 표시 (TTL, 우선순위 등)
  - 강력한 오류 처리 및 디버깅 정보

### feature/web-interface
- **웹 인터페이스**:
  - 직관적인 사용자 인터페이스로 모든 기능에 접근 가능
  - Ping 테스트, 포트 스캔, DNS 조회를 웹에서 실행
  - 실시간 결과 표시 및 포맷팅
  - 반응형 디자인으로 다양한 기기에서 사용 가능
  - 사용자 친화적인 폼 검증 및 에러 처리

### feature/monitor
- **주기적 모니터링 및 알림 기능**:
  - 여러 호스트와 서비스의 상태를 주기적으로 모니터링
  - 설정 가능한 확인 간격 및 알림 임계값
  - 다양한 알림 방식 지원 (이메일, 로그 파일, 콘솔)
  - 문제 발생 및 복구 시 자동 알림
  - YAML 기반 설정 파일로 쉬운 구성 관리

### feature/docker
- **Docker 컨테이너화**:
  - 애플리케이션의 컨테이너화로 쉬운 배포 및 실행
  - Docker Compose를 통한 웹 인터페이스와 모니터링 서비스 통합 실행
  - 다양한 환경에서 일관된 실행 환경 제공
  - 호스트 머신과의 네트워크 연동 지원

## 설치 방법

### 요구사항

- Python 3.6 이상
- pip (Python 패키지 관리자)
- Docker 및 Docker Compose (Docker를 이용한 실행 시)

### 설치 단계

1. 저장소 클론 또는 다운로드:
   ```bash
   git clone https://github.com/DevOpsLab-OZ/network_monitor.git
   cd network-monitor
   ```

2. 가상환경 생성 및 활성화:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 사용 방법

### 명령행 인터페이스

#### Ping 테스트

호스트에 대한 Ping 테스트를 실행하려면:

```bash
python app.py ping google.com
```

옵션:
- `-c, --count`: 보낼 ping 패킷 수 (기본값: 5)
- `-t, --timeout`: 타임아웃 시간(초) (기본값: 2)

예시:
```bash
# 10개 패킷, 1초 타임아웃으로 ping 테스트
python app.py ping google.com -c 10 -t 1
```

#### 포트 스캔

호스트의 포트를 스캔하려면:

```bash
python app.py scan google.com
```

옵션:
- `-p, --ports`: 스캔할 포트 범위 (예: 1-1024)
- `--common`: 일반적인 포트만 스캔
- `-t, --timeout`: 각 포트에 대한 타임아웃 시간(초) (기본값: 0.5)

예시:
```bash
# 포트 20-100 범위 스캔
python app.py scan localhost -p 20-100

# 일반적인 포트만 스캔
python app.py scan localhost --common

# 더 빠른 스캔을 위해 타임아웃 줄이기
python app.py scan localhost -t 0.2
```

#### DNS 조회

##### 정방향 DNS 조회

도메인 이름에 대한 DNS 레코드를 조회하려면:

```bash
python app.py dns lookup google.com
```

옵션:
- `-t, --type`: 조회할 레코드 타입 (기본값: A)
  - 지원 타입: A, AAAA, MX, NS, TXT, SOA, CNAME
- `--timeout`: 타임아웃 시간(초) (기본값: 2.0)

예시:
```bash
# 메일 서버 조회
python app.py dns lookup gmail.com -t MX

# 네임서버 조회
python app.py dns lookup google.com -t NS

# 상세 SOA 정보 조회
python app.py dns lookup google.com -t SOA
```

##### 역방향 DNS 조회

IP 주소에 대한 호스트 이름을 조회하려면:

```bash
python app.py dns reverse 8.8.8.8
```

옵션:
- `--timeout`: 타임아웃 시간(초) (기본값: 2.0)

예시:
```bash
# 타임아웃 설정
python app.py dns reverse 1.1.1.1 --timeout 3.0
```

### 웹 인터페이스

웹 인터페이스를 시작하려면:

```bash
python web_app.py
```

웹 브라우저에서 다음 URL로 접속합니다:
```
http://localhost:5000
```

웹 인터페이스는 다음 기능을 제공합니다:
- **Ping 테스트**: 호스트의 응답 시간 측정
- **포트 스캔**: 특정 호스트의 열린 포트 확인
- **DNS 조회**: 도메인 이름에 대한 DNS 레코드 조회 및 역방향 DNS 조회

### 주기적 모니터링

모니터링 도구를 시작하려면:

```bash
python monitor.py
```

최초 실행 시 기본 설정 파일(`monitor_config.yaml`)이 생성됩니다. 이 파일을 편집하여 모니터링할 호스트, 확인 간격, 알림 방법 등을 설정할 수 있습니다.

#### 설정 파일 예시

```yaml
monitors:
  - name: "Google DNS 테스트"
    type: "ping"
    host: "8.8.8.8"
    count: 3
    timeout: 1
    check_interval: 300  # 5분마다 확인
    alert_threshold: 2   # 2번 연속 실패 시 알림

  - name: "웹 서버 테스트"
    type: "port"
    host: "example.com"
    port: 80
    timeout: 1
    check_interval: 60   # 1분마다 확인
    alert_threshold: 3   # 3번 연속 실패 시 알림

alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "your-email@gmail.com"
    sender_password: "your-password"
    recipient_email: "recipient@example.com"
  log:
    enabled: true
    file: "monitor.log"
  console:
    enabled: true
```

## Docker를 이용한 실행 방법

### Docker 이미지 빌드 및 실행

1. Docker 이미지 빌드:
   ```bash
   docker build -t network-monitor .
   ```

2. Docker 컨테이너 실행 (웹 인터페이스):
   ```bash
   docker run -p 5000:5000 network-monitor
   ```

3. Docker 컨테이너 실행 (모니터링 서비스):
   ```bash
   docker run network-monitor python monitor.py
   ```

### Docker Compose를 이용한 실행

웹 인터페이스와 모니터링 서비스를 함께 실행하려면:

```bash
docker compose up
```

백그라운드에서 실행하려면:

```bash
docker compose up -d
```

실행 중인 서비스 확인:

```bash
docker compose ps
```

서비스 중지:

```bash
docker compose down
```

### 컨테이너 내부에서 명령행 도구 사용

```bash
docker run network-monitor python app.py ping google.com
docker run network-monitor python app.py scan localhost --common
docker run network-monitor python app.py dns lookup google.com -t A
```

### 주의사항

- 컨테이너 내부에서 localhost를 스캔하면 호스트 머신이 아닌 컨테이너 자체를 스캔합니다.
- 호스트 머신을 스캔하려면 Docker의 호스트 네트워크 모드를 사용하세요:
  ```bash
  docker run --network host network-monitor python app.py scan localhost
  ```

## 프로젝트 구조

```
network_monitor/
├── network_monitor/       # 메인 패키지
│   ├── __init__.py        # 패키지 초기화 파일
│   ├── ping_monitor.py    # Ping 모니터링 모듈
│   ├── port_scanner.py    # 포트 스캔 모듈
│   ├── dns_lookup.py      # DNS 조회 모듈
│   ├── utils.py           # 유틸리티 함수들
│   └── config.py          # 설정 관리
├── app.py                 # 명령행 인터페이스
├── web_app.py             # 웹 인터페이스
├── monitor.py             # 주기적 모니터링 및 알림
├── templates/             # 웹 템플릿 디렉토리
│   └── index.html         # 메인 웹 페이지
├── Dockerfile             # Docker 이미지 빌드 설정
├── docker-compose.yml     # Docker Compose 구성 파일
├── .dockerignore          # Docker 빌드 제외 파일 목록
├── monitor_config.yaml    # 모니터링 설정 파일
├── monitor.log            # 모니터링 로그 파일
├── requirements.txt       # 필요한 패키지 목록
└── README.md              # 프로젝트 설명
```

## 향후 개발 계획

- 결과 데이터베이스 저장 및 이력 조회 기능
- 네트워크 트래픽 분석 기능
- 더 풍부한 시각화 및 대시보드
- API 엔드포인트 제공
- 테스트 코드 작성 및 CI/CD 파이프라인 구축

## 기여 방법

이 프로젝트는 개발 진행 중입니다. 기여하고 싶으시다면:

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 만듭니다: `git checkout -b feature/amazing-feature`
3. 변경사항을 커밋합니다: `git commit -m 'Add some amazing feature'`
4. 브랜치에 푸시합니다: `git push origin feature/amazing-feature`
5. Pull Request를 제출합니다.

## 라이센스

MIT License
