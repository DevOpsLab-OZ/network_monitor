#!/usr/bin/env python3
import socket
import threading
import os
from datetime import datetime

class FileTransferServer:
    def __init__(self, host='localhost', port=8082, upload_dir='uploads'):
        self.host = host
        self.port = port
        self.upload_dir = upload_dir
        self.socket = None
        self.running = False
        
        # 업로드 디렉토리 생성
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
            
    def start(self):
        """파일 전송 서버 시작"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"File Transfer Server started on {self.host}:{self.port}")
            print(f"Upload directory: {os.path.abspath(self.upload_dir)}")
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
            # 클라이언트로부터 파일명 받기
            filename_data = client_socket.recv(1024)
            if not filename_data:
                return
                
            filename = filename_data.decode('utf-8').strip()
            if not filename:
                client_socket.send(b"ERROR: No filename provided")
                return
                
            # 안전한 파일명 생성 (경로 조작 방지)
            safe_filename = os.path.basename(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_filename = f"{timestamp}_{safe_filename}"
            filepath = os.path.join(self.upload_dir, full_filename)
            
            # 파일 크기 받기
            size_data = client_socket.recv(16)
            if not size_data:
                client_socket.send(b"ERROR: No file size provided")
                return
                
            try:
                file_size = int(size_data.decode('utf-8').strip())
            except ValueError:
                client_socket.send(b"ERROR: Invalid file size")
                return
                
            print(f"Receiving file '{safe_filename}' ({file_size} bytes) from {client_address}")
            
            # 파일 수신 시작 응답
            client_socket.send(b"READY")
            
            # 파일 데이터 받기
            received_size = 0
            with open(filepath, 'wb') as f:
                while received_size < file_size:
                    chunk_size = min(4096, file_size - received_size)
                    chunk = client_socket.recv(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    received_size += len(chunk)
                    
            if received_size == file_size:
                success_msg = f"SUCCESS: File '{full_filename}' received ({received_size} bytes)"
                client_socket.send(success_msg.encode('utf-8'))
                print(f"File '{full_filename}' saved successfully")
            else:
                error_msg = f"ERROR: File transfer incomplete ({received_size}/{file_size} bytes)"
                client_socket.send(error_msg.encode('utf-8'))
                print(f"File transfer failed: {error_msg}")
                
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            try:
                client_socket.send(error_msg.encode('utf-8'))
            except:
                pass
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection with {client_address} closed")
            
    def stop(self):
        """서버 중지"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("File Transfer Server stopped")

def run_file_transfer_server(host='localhost', port=8082, upload_dir='uploads'):
    """파일 전송 서버 실행"""
    server = FileTransferServer(host, port, upload_dir)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='File Transfer Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8082, help='Port to bind to')
    parser.add_argument('--upload-dir', default='uploads', help='Directory to store uploaded files')
    
    args = parser.parse_args()
    
    run_file_transfer_server(args.host, args.port, args.upload_dir)