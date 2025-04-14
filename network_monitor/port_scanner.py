import socket
from concurrent.futures import ThreadPoolExecutor
import time
from .config import DEFAULT_PORT_RANGE, DEFAULT_TIMEOUT

def scan_port(host, port, timeout=DEFAULT_TIMEOUT):
    """
    지정된 호스트의 특정 포트가 열려 있는지 확인합니다.
    
    Args:
        host (str): 스캔할 호스트 이름 또는 IP 주소
        port (int): 스캔할 포트 번호
        timeout (float): 연결 타임아웃 시간(초)
        
    Returns:
        tuple: (port, is_open, service_name)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        # 연결 시도
        start_time = time.time()
        result = sock.connect_ex((host, port))
        response_time = time.time() - start_time
        
        # 서비스 이름 가져오기 시도
        try:
            service_name = socket.getservbyport(port)
        except (socket.error, OSError):
            service_name = "unknown"
        
        if result == 0:
            return (port, True, service_name, response_time)
        else:
            return (port, False, None, None)
    except socket.error:
        return (port, False, None, None)
    finally:
        sock.close()

def scan_host(host, port_range=DEFAULT_PORT_RANGE, timeout=DEFAULT_TIMEOUT, max_workers=50):
    """
    지정된 호스트의 포트 범위를 스캔합니다.
    
    Args:
        host (str): 스캔할 호스트 이름 또는 IP 주소
        port_range (tuple): 스캔할 포트 범위 (시작, 끝)
        timeout (float): 연결 타임아웃 시간(초)
        max_workers (int): 동시에 실행할 최대 스레드 수
        
    Returns:
        dict: 포트 스캔 결과를 포함하는 딕셔너리
    """
    start_port, end_port = port_range
    ports_to_scan = range(start_port, end_port + 1)
    open_ports = []
    
    print(f"Scanning {host} for open ports from {start_port} to {end_port}...")
    start_time = time.time()
    
    # 스레드 풀을 사용하여 병렬로 포트 스캔
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # scan_port 함수에 인자를 전달하여 실행
        scan_results = list(executor.map(
            lambda p: scan_port(host, p, timeout), 
            ports_to_scan
        ))
    
    # 결과 처리
    for port, is_open, service_name, response_time in scan_results:
        if is_open:
            print(f"Port {port} is open ({service_name}) - Response time: {response_time:.4f}s")
            open_ports.append({
                'port': port,
                'service': service_name,
                'response_time': response_time
            })
    
    total_time = time.time() - start_time
    
    return {
        'host': host,
        'start_port': start_port,
        'end_port': end_port,
        'total_ports_scanned': len(ports_to_scan),
        'open_ports': open_ports,
        'open_port_count': len(open_ports),
        'scan_time': total_time
    }

def get_common_ports():
    """
    일반적으로 사용되는 포트 목록을 반환합니다.
    
    Returns:
        list: 일반적인 포트 번호 목록
    """
    return [
        21,    # FTP
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        53,    # DNS
        80,    # HTTP
        110,   # POP3
        115,   # SFTP
        135,   # MS RPC
        139,   # NetBIOS
        143,   # IMAP
        194,   # IRC
        443,   # HTTPS
        445,   # SMB
        1433,  # MS SQL
        3306,  # MySQL
        3389,  # RDP
        5432,  # PostgreSQL
        5900,  # VNC
        8080   # HTTP Alternate
    ]
