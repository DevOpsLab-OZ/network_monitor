from ping3 import ping
import time
from .config import DEFAULT_PING_COUNT, DEFAULT_TIMEOUT

def ping_host(host, count=DEFAULT_PING_COUNT, timeout=DEFAULT_TIMEOUT):
    """
    지정된 호스트에 ping을 보내고 결과를 반환합니다.
    
    Args:
        host (str): ping을 보낼 호스트 이름 또는 IP 주소
        count (int): 보낼 ping 패킷 수
        timeout (int): 타임아웃 시간(초)
        
    Returns:
        dict: ping 결과를 포함하는 딕셔너리
    """
    results = []
    packet_loss = 0
    
    print(f"Pinging {host} {count} times with timeout {timeout}s...")
    
    for i in range(count):
        start_time = time.time()
        response_time = ping(host, timeout=timeout, unit='ms')
        end_time = time.time()
        
        if response_time is None:
            packet_loss += 1
            results.append({
                'seq': i,
                'success': False,
                'time': None,
                'error': 'Request timed out'
            })
            print(f"Ping {i+1}/{count}: Failed (Request timed out)")
        else:
            results.append({
                'seq': i,
                'success': True,
                'time': response_time,
                'error': None
            })
            print(f"Ping {i+1}/{count}: Success ({response_time:.2f} ms)")
        
        # 연속 ping 사이에 약간의 간격 추가
        if i < count - 1:
            time.sleep(0.5)
    
    # 결과 통계 계산
    successful_pings = [r['time'] for r in results if r['success']]
    
    if successful_pings:
        min_time = min(successful_pings)
        max_time = max(successful_pings)
        avg_time = sum(successful_pings) / len(successful_pings)
    else:
        min_time = max_time = avg_time = None
    
    packet_loss_percent = (packet_loss / count) * 100
    
    return {
        'host': host,
        'transmitted': count,
        'received': count - packet_loss,
        'packet_loss': packet_loss,
        'packet_loss_percent': packet_loss_percent,
        'min_time': min_time,
        'max_time': max_time,
        'avg_time': avg_time,
        'results': results
    }

def ping_multiple_hosts(hosts, count=DEFAULT_PING_COUNT, timeout=DEFAULT_TIMEOUT):
    """
    여러 호스트에 ping을 보내고 결과를 반환합니다.
    
    Args:
        hosts (list): ping을 보낼 호스트 이름 또는 IP 주소 목록
        count (int): 각 호스트별 보낼 ping 패킷 수
        timeout (int): 타임아웃 시간(초)
        
    Returns:
        dict: 호스트별 ping 결과를 포함하는 딕셔너리
    """
    results = {}
    
    for host in hosts:
        results[host] = ping_host(host, count, timeout)
    
    return results
