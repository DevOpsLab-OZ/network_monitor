import socket
from concurrent.futures import ThreadPoolExecutor
import time
import select
from .config import DEFAULT_PORT_RANGE, DEFAULT_TIMEOUT
from .socket_options import NonBlockingSocketManager, AdvancedSocketOptions
from .timeout_manager import global_connection_manager, AdaptiveTimeoutManager

def scan_port(host, port, timeout=DEFAULT_TIMEOUT, use_advanced_options=False, use_adaptive_timeout=False):
    """
    지정된 호스트의 특정 포트가 열려 있는지 확인합니다.
    
    Args:
        host (str): 스캔할 호스트 이름 또는 IP 주소
        port (int): 스캔할 포트 번호
        timeout (float): 연결 타임아웃 시간(초)
        use_advanced_options (bool): 고급 소켓 옵션 사용 여부
        use_adaptive_timeout (bool): 적응형 타임아웃 사용 여부
        
    Returns:
        tuple: (port, is_open, service_name, response_time)
    """
    # 적응형 타임아웃 사용 시 호스트별 최적 타임아웃 계산
    if use_adaptive_timeout:
        adaptive_timeout = global_connection_manager.get_timeout_for_host(host)
        actual_timeout = min(timeout, adaptive_timeout) if timeout else adaptive_timeout
    else:
        actual_timeout = timeout
    
    if use_advanced_options:
        result = scan_port_nonblocking(host, port, actual_timeout)
    else:
        result = scan_port_basic(host, port, actual_timeout)
    
    # 적응형 타임아웃 사용 시 결과 기록
    if use_adaptive_timeout:
        port, is_open, service_name, response_time = result
        global_connection_manager.record_host_response(host, response_time, is_open)
    
    return result


def scan_port_basic(host, port, timeout=DEFAULT_TIMEOUT):
    """기본 블로킹 소켓을 사용한 포트 스캔"""
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


def scan_port_nonblocking(host, port, timeout=DEFAULT_TIMEOUT):
    """논블로킹 소켓을 사용한 고성능 포트 스캔"""
    try:
        # 고급 소켓 옵션으로 소켓 생성
        sock = AdvancedSocketOptions.create_socket_with_options(
            blocking=False,
            reuse_addr=True,
            nodelay=True
        )
        
        start_time = time.time()
        
        # 논블로킹 연결 시도
        try:
            sock.connect((host, port))
            # 즉시 연결되는 경우 (보통 localhost)
            response_time = time.time() - start_time
            service_name = get_service_name(port)
            sock.close()
            return (port, True, service_name, response_time)
        except socket.error as e:
            if e.errno not in (socket.errno.EINPROGRESS, socket.errno.EALREADY, socket.errno.EWOULDBLOCK):
                # 연결 불가능한 경우
                sock.close()
                return (port, False, None, None)
        
        # select를 사용하여 연결 완료 대기
        ready = select.select([], [sock], [sock], timeout)
        
        if ready[1] or ready[2]:  # 쓰기 가능하거나 에러 발생
            # 연결 상태 확인
            error = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            response_time = time.time() - start_time
            
            if error == 0:
                # 연결 성공
                service_name = get_service_name(port)
                sock.close()
                return (port, True, service_name, response_time)
            else:
                # 연결 실패
                sock.close()
                return (port, False, None, None)
        else:
            # 타임아웃
            sock.close()
            return (port, False, None, None)
            
    except Exception:
        return (port, False, None, None)


def get_service_name(port):
    """포트 번호에 대한 서비스 이름 조회"""
    try:
        return socket.getservbyport(port)
    except (socket.error, OSError):
        return "unknown"

def scan_host(host, port_range=DEFAULT_PORT_RANGE, timeout=DEFAULT_TIMEOUT, max_workers=50, 
              use_advanced_options=False, use_adaptive_timeout=False):
    """
    지정된 호스트의 포트 범위를 스캔합니다.
    
    Args:
        host (str): 스캔할 호스트 이름 또는 IP 주소
        port_range (tuple): 스캔할 포트 범위 (시작, 끝)
        timeout (float): 연결 타임아웃 시간(초)
        max_workers (int): 동시에 실행할 최대 스레드 수
        use_advanced_options (bool): 고급 소켓 옵션 사용 여부
        use_adaptive_timeout (bool): 적응형 타임아웃 사용 여부
        
    Returns:
        dict: 포트 스캔 결과를 포함하는 딕셔너리
    """
    start_port, end_port = port_range
    ports_to_scan = range(start_port, end_port + 1)
    open_ports = []
    
    # 스캔 방법 표시
    methods = []
    if use_advanced_options:
        methods.append("논블로킹 소켓")
    else:
        methods.append("기본 소켓")
    
    if use_adaptive_timeout:
        methods.append("적응형 타임아웃")
    
    scan_method = " + ".join(methods)
    print(f"Scanning {host} for open ports from {start_port} to {end_port}... ({scan_method})")
    
    # 적응형 타임아웃 사용 시 초기 타임아웃 정보 표시
    if use_adaptive_timeout:
        initial_timeout = global_connection_manager.get_timeout_for_host(host)
        print(f"Initial adaptive timeout for {host}: {initial_timeout:.3f}s")
    
    start_time = time.time()
    
    # 스레드 풀을 사용하여 병렬로 포트 스캔
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # scan_port 함수에 인자를 전달하여 실행
        scan_results = list(executor.map(
            lambda p: scan_port(host, p, timeout, use_advanced_options, use_adaptive_timeout), 
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
    
    # 적응형 타임아웃 사용 시 통계 정보 포함
    result = {
        'host': host,
        'start_port': start_port,
        'end_port': end_port,
        'total_ports_scanned': len(ports_to_scan),
        'open_ports': open_ports,
        'open_port_count': len(open_ports),
        'scan_time': total_time,
        'scan_method': scan_method
    }
    
    if use_adaptive_timeout:
        timeout_stats = global_connection_manager.get_host_manager(host).get_timeout_stats()
        result['timeout_stats'] = timeout_stats
        print(f"Adaptive timeout stats - Avg response: {timeout_stats['avg_response_time']:.3f}s, "
              f"Success rate: {timeout_stats['success_rate']:.2%}, "
              f"Final timeout: {timeout_stats['current_timeout']:.3f}s")
    
    return result

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
