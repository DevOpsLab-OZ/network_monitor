import socket
import threading
from datetime import datetime

class UDPEchoServer:
    def __init__(self, host='localhost', port=8081):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def start(self):
        """UDP 에코 서버 시작"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.running = True
            
            print(f"UDP Echo Server started on {self.host}:{self.port}")
            print("Waiting for messages...")
            
            while self.running:
                try:
                    data, client_address = self.socket.recvfrom(1024)
                    
                    # 받은 데이터를 그대로 에코
                    message = data.decode('utf-8', errors='ignore')
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    echo_message = f"[{timestamp}] Echo: {message}"
                    
                    print(f"Received from {client_address}: {message.strip()}")
                    self.socket.sendto(echo_message.encode('utf-8'), client_address)
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """서버 중지"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("UDP Server stopped")

def run_udp_echo_server(host='localhost', port=8081):
    """UDP 에코 서버 실행"""
    server = UDPEchoServer(host, port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='UDP Echo Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8081, help='Port to bind to')
    
    args = parser.parse_args()
    
    run_udp_echo_server(args.host, args.port)