# 네트워크 모니터링 도구 - feature/ping

이 프로젝트는 Python을 사용한 간단한 네트워크 모니터링 도구입니다. 기본적인 네트워크 진단 기능을 제공하여 네트워크 상태를 파악하고 문제를 진단하는 데 도움을 줍니다.

## feature/ping

- **기본 프로젝트 구조 설정**
- **Ping 테스트 기능**:
  - 특정 호스트의 응답 시간 측정
  - 패킷 손실률 계산
  - 최소/최대/평균 응답 시간 통계

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

## 프로젝트 구조

```
network_monitor/
├── network_monitor/       # 메인 패키지
│   ├── __init__.py        # 패키지 초기화 파일
│   ├── ping_monitor.py    # Ping 모니터링 모듈
│   ├── port_scanner.py    # (향후 구현) 포트 스캔 모듈
│   ├── dns_lookup.py      # (향후 구현) DNS 조회 모듈
│   ├── utils.py           # (향후 구현) 유틸리티 함수들
│   └── config.py          # 설정 관리
├── app.py                 # 명령행 인터페이스
├── requirements.txt       # 필요한 패키지 목록
└── README.md              # 프로젝트 설명
```

## 향후 개발 계획

- 포트 스캔 기능 추가
- DNS 조회 기능 구현
- 웹 인터페이스 개발
- 주기적 모니터링 및 알림 기능

## 기여 방법

이 프로젝트는 개발 초기 단계입니다. 기여하고 싶으시다면:

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 만듭니다: `git checkout -b feature/amazing-feature`
3. 변경사항을 커밋합니다: `git commit -m 'Add some amazing feature'`
4. 브랜치에 푸시합니다: `git push origin feature/amazing-feature`
5. Pull Request를 제출합니다.

## 라이센스

MIT License
