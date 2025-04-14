# 네트워크 모니터링 도구 - feature/dns

이 프로젝트는 Python을 사용한 간단한 네트워크 모니터링 도구입니다. 기본적인 네트워크 진단 기능을 제공하여 네트워크 상태를 파악하고 문제를 진단하는 데 도움을 줍니다.

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

## 설치 방법

### 요구사항

- Python 3.6 이상
- pip (Python 패키지 관리자)

### 설치 단계

1. 저장소 클론 또는 다운로드:
   ```bash
   git clone https://github.com/DevOpsLab-OZ/network-monitor.git
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

### Ping 테스트

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

### 포트 스캔

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

### DNS 조회

#### 정방향 DNS 조회

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

#### 역방향 DNS 조회

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

## 프로젝트 구조

```
network_monitor/
├── network_monitor/       # 메인 패키지
│   ├── __init__.py        # 패키지 초기화 파일
│   ├── ping_monitor.py    # Ping 모니터링 모듈
│   ├── port_scanner.py    # 포트 스캔 모듈
│   ├── dns_lookup.py      # DNS 조회 모듈
│   ├── utils.py           # (향후 구현) 유틸리티 함수들
│   └── config.py          # 설정 관리
├── app.py                 # 명령행 인터페이스
├── requirements.txt       # 필요한 패키지 목록
└── README.md              # 프로젝트 설명
```

## 향후 개발 계획

- 웹 인터페이스 개발
- 주기적 모니터링 및 알림 기능
- 결과 저장 및 리포팅 기능
- 네트워크 트래픽 분석 기능

## 기여 방법

이 프로젝트는 개발 진행 중입니다. 기여하고 싶으시다면:

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 만듭니다: `git checkout -b feature/amazing-feature`
3. 변경사항을 커밋합니다: `git commit -m 'Add some amazing feature'`
4. 브랜치에 푸시합니다: `git push origin feature/amazing-feature`
5. Pull Request를 제출합니다.

## 라이센스

MIT License
