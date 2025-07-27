import time
import signal
import threading
from typing import Optional, Callable, Any
from contextlib import contextmanager


class TimeoutError(Exception):
    """타임아웃 발생 시 발생하는 예외"""
    pass


class PreciseTimeoutManager:
    """정밀한 타임아웃 제어를 위한 매니저 클래스"""
    
    def __init__(self):
        self.active_timeouts = {}
        self.timeout_counter = 0
        self.lock = threading.Lock()
    
    @contextmanager
    def timeout(self, seconds: float, error_message: str = "Operation timed out"):
        """
        정밀한 타임아웃 컨텍스트 매니저
        
        Args:
            seconds: 타임아웃 시간 (초, 소수점 지원)
            error_message: 타임아웃 시 에러 메시지
        """
        start_time = time.time()
        timeout_id = None
        
        def timeout_handler():
            elapsed = time.time() - start_time
            if elapsed >= seconds:
                raise TimeoutError(f"{error_message} (after {elapsed:.3f}s)")
        
        try:
            with self.lock:
                self.timeout_counter += 1
                timeout_id = self.timeout_counter
                self.active_timeouts[timeout_id] = {
                    'start_time': start_time,
                    'timeout_seconds': seconds,
                    'handler': timeout_handler
                }
            
            yield timeout_handler
            
        finally:
            if timeout_id and timeout_id in self.active_timeouts:
                with self.lock:
                    del self.active_timeouts[timeout_id]
    
    def check_timeout(self, timeout_id: int) -> bool:
        """특정 타임아웃 ID의 상태 확인"""
        with self.lock:
            if timeout_id not in self.active_timeouts:
                return False
            
            timeout_info = self.active_timeouts[timeout_id]
            elapsed = time.time() - timeout_info['start_time']
            return elapsed >= timeout_info['timeout_seconds']
    
    def get_remaining_time(self, timeout_id: int) -> float:
        """특정 타임아웃 ID의 남은 시간 반환"""
        with self.lock:
            if timeout_id not in self.active_timeouts:
                return 0.0
            
            timeout_info = self.active_timeouts[timeout_id]
            elapsed = time.time() - timeout_info['start_time']
            remaining = timeout_info['timeout_seconds'] - elapsed
            return max(0.0, remaining)


class AdaptiveTimeoutManager:
    """적응형 타임아웃 매니저 - 네트워크 상태에 따라 타임아웃 조정"""
    
    def __init__(self, base_timeout: float = 5.0, min_timeout: float = 0.1, max_timeout: float = 30.0):
        self.base_timeout = base_timeout
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout
        self.response_times = []
        self.success_rate = 1.0
        self.lock = threading.Lock()
    
    def record_response(self, response_time: Optional[float], success: bool):
        """응답 시간과 성공 여부 기록"""
        with self.lock:
            if response_time is not None:
                self.response_times.append(response_time)
                # 최근 100개 응답만 유지
                if len(self.response_times) > 100:
                    self.response_times.pop(0)
            
            # 성공률 계산 (최근 20회 기준)
            recent_count = min(20, len(self.response_times))
            if recent_count > 0:
                recent_successes = sum(1 for _ in range(recent_count) if success)
                self.success_rate = recent_successes / recent_count
    
    def get_adaptive_timeout(self, target_host: str = "") -> float:
        """적응형 타임아웃 값 계산"""
        with self.lock:
            if not self.response_times:
                return self.base_timeout
            
            # 평균 응답 시간 계산
            avg_response_time = sum(self.response_times) / len(self.response_times)
            
            # 95퍼센타일 응답 시간 계산
            sorted_times = sorted(self.response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index] if sorted_times else avg_response_time
            
            # 적응형 타임아웃 계산
            # 성공률이 낮으면 타임아웃을 늘리고, 높으면 줄임
            success_factor = 2.0 - self.success_rate  # 0.5 ~ 2.0 범위
            adaptive_timeout = p95_response_time * 3 * success_factor
            
            # 최소/최대 범위 내로 제한
            adaptive_timeout = max(self.min_timeout, min(self.max_timeout, adaptive_timeout))
            
            return adaptive_timeout
    
    def get_timeout_stats(self) -> dict:
        """타임아웃 통계 정보 반환"""
        with self.lock:
            if not self.response_times:
                return {
                    'count': 0,
                    'avg_response_time': 0.0,
                    'success_rate': self.success_rate,
                    'current_timeout': self.base_timeout
                }
            
            return {
                'count': len(self.response_times),
                'avg_response_time': sum(self.response_times) / len(self.response_times),
                'min_response_time': min(self.response_times),
                'max_response_time': max(self.response_times),
                'success_rate': self.success_rate,
                'current_timeout': self.get_adaptive_timeout()
            }


class ConnectionTimeoutManager:
    """연결별 타임아웃 관리"""
    
    def __init__(self):
        self.connection_timeouts = {}
        self.host_managers = {}
        self.lock = threading.Lock()
    
    def get_host_manager(self, host: str) -> AdaptiveTimeoutManager:
        """호스트별 적응형 타임아웃 매니저 반환"""
        with self.lock:
            if host not in self.host_managers:
                self.host_managers[host] = AdaptiveTimeoutManager()
            return self.host_managers[host]
    
    def get_timeout_for_host(self, host: str) -> float:
        """특정 호스트에 대한 적응형 타임아웃 반환"""
        manager = self.get_host_manager(host)
        return manager.get_adaptive_timeout(host)
    
    def record_host_response(self, host: str, response_time: Optional[float], success: bool):
        """호스트별 응답 기록"""
        manager = self.get_host_manager(host)
        manager.record_response(response_time, success)
    
    def get_all_host_stats(self) -> dict:
        """모든 호스트의 타임아웃 통계 반환"""
        with self.lock:
            stats = {}
            for host, manager in self.host_managers.items():
                stats[host] = manager.get_timeout_stats()
            return stats


# 전역 인스턴스
global_timeout_manager = PreciseTimeoutManager()
global_connection_manager = ConnectionTimeoutManager()


def with_timeout(seconds: float, error_message: str = "Operation timed out"):
    """
    함수 데코레이터로 타임아웃 적용
    
    Args:
        seconds: 타임아웃 시간 (초)
        error_message: 타임아웃 시 에러 메시지
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            with global_timeout_manager.timeout(seconds, error_message):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def sleep_with_timeout_check(seconds: float, check_interval: float = 0.1, timeout_checker: Optional[Callable] = None):
    """
    타임아웃 체크가 가능한 sleep 함수
    
    Args:
        seconds: 대기 시간
        check_interval: 타임아웃 체크 간격
        timeout_checker: 타임아웃 체크 함수
    """
    elapsed = 0.0
    while elapsed < seconds:
        if timeout_checker and timeout_checker():
            raise TimeoutError("Sleep interrupted by timeout")
        
        sleep_time = min(check_interval, seconds - elapsed)
        time.sleep(sleep_time)
        elapsed += sleep_time


class ProgressiveTimeoutManager:
    """점진적 타임아웃 매니저 - 시도 횟수에 따라 타임아웃 증가"""
    
    def __init__(self, initial_timeout: float = 1.0, max_timeout: float = 10.0, backoff_factor: float = 1.5):
        self.initial_timeout = initial_timeout
        self.max_timeout = max_timeout
        self.backoff_factor = backoff_factor
        self.attempt_counts = {}
        self.lock = threading.Lock()
    
    def get_timeout_for_attempt(self, key: str, attempt: int = 0) -> float:
        """시도 횟수에 따른 점진적 타임아웃 계산"""
        timeout = self.initial_timeout * (self.backoff_factor ** attempt)
        return min(timeout, self.max_timeout)
    
    def record_attempt(self, key: str, success: bool):
        """시도 기록"""
        with self.lock:
            if key not in self.attempt_counts:
                self.attempt_counts[key] = {'attempts': 0, 'successes': 0}
            
            self.attempt_counts[key]['attempts'] += 1
            if success:
                self.attempt_counts[key]['successes'] += 1
                # 성공 시 카운터 리셋
                self.attempt_counts[key]['attempts'] = 0
    
    def get_next_timeout(self, key: str) -> float:
        """다음 시도를 위한 타임아웃 반환"""
        with self.lock:
            if key not in self.attempt_counts:
                return self.initial_timeout
            
            attempts = self.attempt_counts[key]['attempts']
            return self.get_timeout_for_attempt(key, attempts)