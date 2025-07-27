import socket
import threading
import time
from datetime import datetime
from .socket_options import AdvancedSocketOptions

class TCPEchoServer:
    def __init__(self, host='localhost', port=8080, use_advanced_options=True):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = []
        self.use_advanced_options = use_advanced_options
        
    def start_single_client_server(self):
        """단일 클라이언트 TCP 에코 서버 시작"""
        try:
            if self.use_advanced_options:
                self.socket = AdvancedSocketOptions.create_optimized_server_socket(
                    self.host, 
                    self.port, 
                    backlog=1,
                    keepalive=True,
                    nodelay=True
                )
                print("Advanced socket options enabled: SO_REUSEADDR, SO_KEEPALIVE, TCP_NODELAY")
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind((self.host, self.port))
                self.socket.listen(1)
            self.running = True
            
            print(f"TCP Echo Server (Single Client) started on {self.host}:{self.port}")
            print("Waiting for connection...")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"Connection from {client_address}")
                    
                    self._handle_client(client_socket, client_address)
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
            
    def start_multi_client_server(self):
        """멀티 클라이언트 TCP 에코 서버 시작"""
        try:
            if self.use_advanced_options:
                self.socket = AdvancedSocketOptions.create_optimized_server_socket(
                    self.host, 
                    self.port, 
                    backlog=5,
                    keepalive=True,
                    nodelay=False  # 멀티 클라이언트에서는 처리량 우선
                )
                print("Advanced socket options enabled: SO_REUSEADDR, SO_KEEPALIVE")
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind((self.host, self.port))
                self.socket.listen(5)
            self.running = True
            
            print(f"TCP Echo Server (Multi Client) started on {self.host}:{self.port}")
            print("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"New connection from {client_address}")
                    
                    # 각 클라이언트를 별도 스레드에서 처리
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    self.clients.append(client_thread)
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
            
    def _handle_client(self, client_socket, client_address):
        """클라이언트 연결 처리"""
        try:
            # 클라이언트 소켓에도 Keep-alive 설정 (서버가 고급 옵션 사용 시)
            if self.use_advanced_options:
                client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # 소켓 옵션 정보 출력
                options = AdvancedSocketOptions.get_socket_options(client_socket)
                print(f"Client {client_address} socket options: SO_KEEPALIVE={options.get('SO_KEEPALIVE', 'N/A')}")
            
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                # 받은 데이터를 그대로 에코
                message = data.decode('utf-8', errors='ignore')
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                echo_message = f"[{timestamp}] Echo: {message}"
                
                print(f"Received from {client_address}: {message.strip()}")
                client_socket.send(echo_message.encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection with {client_address} closed")
            
    def stop(self):
        """서버 중지"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("Server stopped")

def run_tcp_echo_server(host='localhost', port=8080, multi_client=False, advanced_options=False):
    """TCP 에코 서버 실행"""
    server = TCPEchoServer(host, port, use_advanced_options=advanced_options)
    
    try:
        if multi_client:
            server.start_multi_client_server()
        else:
            server.start_single_client_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TCP Echo Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--multi', action='store_true', help='Enable multi-client support')
    parser.add_argument('--advanced', action='store_true', help='Use advanced socket options (SO_KEEPALIVE, etc.)')
    
    args = parser.parse_args()
    
    run_tcp_echo_server(args.host, args.port, args.multi, args.advanced)