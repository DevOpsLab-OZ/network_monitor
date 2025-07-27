import socket
import time
from typing import Dict, Any, Optional


class AdvancedSocketOptions:
    """고급 소켓 옵션 설정 및 관리 클래스"""
    
    def __init__(self):
        self.options = {}
    
    @staticmethod
    def create_socket_with_options(
        family: int = socket.AF_INET,
        socket_type: int = socket.SOCK_STREAM,
        reuse_addr: bool = True,
        keepalive: bool = False,
        keepalive_idle: int = 7200,
        keepalive_interval: int = 75,
        keepalive_probes: int = 9,
        nodelay: bool = False,
        linger: Optional[tuple] = None,
        rcvbuf: Optional[int] = None,
        sndbuf: Optional[int] = None,
        blocking: bool = True
    ) -> socket.socket:
        """
        고급 소켓 옵션이 적용된 소켓 생성
        
        Args:
            family: 소켓 패밀리 (AF_INET, AF_INET6)
            socket_type: 소켓 타입 (SOCK_STREAM, SOCK_DGRAM)
            reuse_addr: SO_REUSEADDR 옵션 활성화
            keepalive: SO_KEEPALIVE 옵션 활성화
            keepalive_idle: TCP_KEEPIDLE 값 (초)
            keepalive_interval: TCP_KEEPINTVL 값 (초)
            keepalive_probes: TCP_KEEPCNT 값
            nodelay: TCP_NODELAY 옵션 (Nagle 알고리즘 비활성화)
            linger: SO_LINGER 옵션 (튜플: (enable, timeout))
            rcvbuf: SO_RCVBUF 크기
            sndbuf: SO_SNDBUF 크기
            blocking: 블로킹 모드 설정
        """
        sock = socket.socket(family, socket_type)
        
        try:
            # SO_REUSEADDR: 주소 재사용 허용
            if reuse_addr:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # SO_KEEPALIVE: TCP 연결 유지 확인
            if keepalive and socket_type == socket.SOCK_STREAM:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                
                # TCP Keep-alive 세부 설정 (Linux/Unix)
                try:
                    if hasattr(socket, 'TCP_KEEPIDLE'):
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, keepalive_idle)
                    if hasattr(socket, 'TCP_KEEPINTVL'):
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, keepalive_interval)
                    if hasattr(socket, 'TCP_KEEPCNT'):
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, keepalive_probes)
                except OSError:
                    # Windows나 다른 플랫폼에서 지원하지 않는 경우
                    pass
            
            # TCP_NODELAY: Nagle 알고리즘 비활성화 (지연 감소)
            if nodelay and socket_type == socket.SOCK_STREAM:
                try:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                except OSError:
                    pass
            
            # SO_LINGER: 소켓 닫을 때 대기 설정
            if linger and isinstance(linger, tuple) and len(linger) == 2:
                import struct
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, 
                              struct.pack('ii', int(linger[0]), int(linger[1])))
            
            # SO_RCVBUF: 수신 버퍼 크기
            if rcvbuf:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcvbuf)
            
            # SO_SNDBUF: 송신 버퍼 크기
            if sndbuf:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, sndbuf)
            
            # 블로킹/논블로킹 모드 설정
            sock.setblocking(blocking)
            
        except Exception as e:
            sock.close()
            raise Exception(f"소켓 옵션 설정 실패: {e}")
        
        return sock
    
    @staticmethod
    def get_socket_options(sock: socket.socket) -> Dict[str, Any]:
        """소켓의 현재 옵션 상태 조회"""
        options = {}
        
        try:
            # 기본 소켓 옵션들
            options['SO_REUSEADDR'] = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
            options['SO_KEEPALIVE'] = sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
            options['SO_RCVBUF'] = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            options['SO_SNDBUF'] = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            
            # TCP 관련 옵션들 (TCP 소켓인 경우)
            if sock.type == socket.SOCK_STREAM:
                try:
                    if hasattr(socket, 'TCP_NODELAY'):
                        options['TCP_NODELAY'] = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
                    if hasattr(socket, 'TCP_KEEPIDLE'):
                        options['TCP_KEEPIDLE'] = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE)
                    if hasattr(socket, 'TCP_KEEPINTVL'):
                        options['TCP_KEEPINTVL'] = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL)
                    if hasattr(socket, 'TCP_KEEPCNT'):
                        options['TCP_KEEPCNT'] = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT)
                except OSError:
                    pass
            
            # 소켓 상태
            options['blocking'] = sock.getblocking()
            options['timeout'] = sock.gettimeout()
            
        except Exception as e:
            options['error'] = str(e)
        
        return options
    
    @staticmethod
    def create_optimized_client_socket(
        target_host: str,
        target_port: int,
        timeout: float = 5.0,
        keepalive: bool = True,
        nodelay: bool = True
    ) -> socket.socket:
        """클라이언트용 최적화된 소켓 생성"""
        sock = AdvancedSocketOptions.create_socket_with_options(
            reuse_addr=True,
            keepalive=keepalive,
            nodelay=nodelay,
            keepalive_idle=600,  # 10분
            keepalive_interval=60,  # 1분
            keepalive_probes=3
        )
        
        sock.settimeout(timeout)
        return sock
    
    @staticmethod
    def create_optimized_server_socket(
        bind_host: str,
        bind_port: int,
        backlog: int = 5,
        keepalive: bool = True,
        nodelay: bool = False
    ) -> socket.socket:
        """서버용 최적화된 소켓 생성"""
        sock = AdvancedSocketOptions.create_socket_with_options(
            reuse_addr=True,
            keepalive=keepalive,
            nodelay=nodelay,
            keepalive_idle=7200,  # 2시간
            keepalive_interval=75,  # 75초
            keepalive_probes=9,
            rcvbuf=65536,  # 64KB
            sndbuf=65536   # 64KB
        )
        
        sock.bind((bind_host, bind_port))
        sock.listen(backlog)
        return sock


class NonBlockingSocketManager:
    """논블로킹 소켓 관리 클래스"""
    
    def __init__(self):
        self.sockets = {}
    
    def create_nonblocking_socket(
        self,
        socket_id: str,
        family: int = socket.AF_INET,
        socket_type: int = socket.SOCK_STREAM
    ) -> socket.socket:
        """논블로킹 소켓 생성 및 등록"""
        sock = AdvancedSocketOptions.create_socket_with_options(
            family=family,
            socket_type=socket_type,
            blocking=False,
            reuse_addr=True
        )
        
        self.sockets[socket_id] = {
            'socket': sock,
            'created_at': time.time(),
            'last_activity': time.time()
        }
        
        return sock
    
    def connect_nonblocking(
        self,
        socket_id: str,
        address: tuple,
        timeout: float = 5.0
    ) -> bool:
        """논블로킹 소켓으로 연결 시도"""
        if socket_id not in self.sockets:
            raise ValueError(f"Socket {socket_id} not found")
        
        sock = self.sockets[socket_id]['socket']
        start_time = time.time()
        
        try:
            sock.connect(address)
            return True
        except socket.error as e:
            if e.errno == socket.errno.EINPROGRESS or e.errno == socket.errno.EALREADY:
                # 연결이 진행 중
                while time.time() - start_time < timeout:
                    try:
                        # 소켓이 쓰기 가능한지 확인 (연결 완료)
                        import select
                        ready = select.select([], [sock], [], 0.1)
                        if ready[1]:
                            # 연결 상태 확인
                            error = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                            if error == 0:
                                self.sockets[socket_id]['last_activity'] = time.time()
                                return True
                            else:
                                raise socket.error(error, "Connection failed")
                    except select.error:
                        break
                    time.sleep(0.01)
                
                raise socket.timeout("Connection timeout")
            else:
                raise
    
    def send_nonblocking(
        self,
        socket_id: str,
        data: bytes,
        timeout: float = 5.0
    ) -> int:
        """논블로킹 소켓으로 데이터 전송"""
        if socket_id not in self.sockets:
            raise ValueError(f"Socket {socket_id} not found")
        
        sock = self.sockets[socket_id]['socket']
        start_time = time.time()
        total_sent = 0
        
        while total_sent < len(data) and time.time() - start_time < timeout:
            try:
                sent = sock.send(data[total_sent:])
                if sent == 0:
                    raise socket.error("Socket connection broken")
                total_sent += sent
                self.sockets[socket_id]['last_activity'] = time.time()
            except socket.error as e:
                if e.errno == socket.errno.EAGAIN or e.errno == socket.errno.EWOULDBLOCK:
                    # 송신 버퍼가 가득참, 잠시 대기
                    time.sleep(0.01)
                    continue
                else:
                    raise
        
        if total_sent < len(data):
            raise socket.timeout("Send timeout")
        
        return total_sent
    
    def recv_nonblocking(
        self,
        socket_id: str,
        buffer_size: int = 1024,
        timeout: float = 5.0
    ) -> bytes:
        """논블로킹 소켓으로 데이터 수신"""
        if socket_id not in self.sockets:
            raise ValueError(f"Socket {socket_id} not found")
        
        sock = self.sockets[socket_id]['socket']
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                data = sock.recv(buffer_size)
                if data:
                    self.sockets[socket_id]['last_activity'] = time.time()
                    return data
                else:
                    raise socket.error("Socket connection closed")
            except socket.error as e:
                if e.errno == socket.errno.EAGAIN or e.errno == socket.errno.EWOULDBLOCK:
                    # 수신할 데이터가 없음, 잠시 대기
                    time.sleep(0.01)
                    continue
                else:
                    raise
        
        raise socket.timeout("Receive timeout")
    
    def close_socket(self, socket_id: str):
        """소켓 닫기 및 등록 해제"""
        if socket_id in self.sockets:
            self.sockets[socket_id]['socket'].close()
            del self.sockets[socket_id]
    
    def cleanup_inactive_sockets(self, max_idle_time: float = 300.0):
        """비활성 소켓 정리 (5분 이상 비활성)"""
        current_time = time.time()
        inactive_sockets = []
        
        for socket_id, info in self.sockets.items():
            if current_time - info['last_activity'] > max_idle_time:
                inactive_sockets.append(socket_id)
        
        for socket_id in inactive_sockets:
            self.close_socket(socket_id)
        
        return len(inactive_sockets)


# 편의 함수들
def create_tcp_server_socket(host: str, port: int, **options) -> socket.socket:
    """TCP 서버 소켓 생성 편의 함수"""
    return AdvancedSocketOptions.create_optimized_server_socket(host, port, **options)


def create_tcp_client_socket(host: str, port: int, **options) -> socket.socket:
    """TCP 클라이언트 소켓 생성 편의 함수"""
    return AdvancedSocketOptions.create_optimized_client_socket(host, port, **options)


def create_udp_socket(host: str = '', port: int = 0, **options) -> socket.socket:
    """UDP 소켓 생성 편의 함수"""
    sock = AdvancedSocketOptions.create_socket_with_options(
        socket_type=socket.SOCK_DGRAM,
        **options
    )
    if host or port:
        sock.bind((host, port))
    return sock