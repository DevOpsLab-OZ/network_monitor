#!/usr/bin/env python3
from network_monitor.ping_monitor import ping_host
from network_monitor.port_scanner import scan_port
import time
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import argparse
from datetime import datetime

# 설정 파일 경로
CONFIG_FILE = 'monitor_config.yaml'
LOG_FILE = 'monitor.log'

def load_config():
    """
    설정 파일을 로드합니다. 파일이 없으면 기본 설정을 생성합니다.
    """
    if not os.path.exists(CONFIG_FILE):
        # 기본 설정 생성
        default_config = {
	   'monitors': [
                {
                    'name': 'Google Web Server',
                    'type': 'ping',
                    'host': 'google.com',
                    'count': 3,
                    'timeout': 2,
                    'check_interval': 300,  # 5분
                    'alert_threshold': 2    # 2번 연속 실패 시 알림
                },
                {
                    'name': 'Local Web Server',
                    'type': 'port',
                    'host': 'localhost',
                    'port': 80,
                    'timeout': 1,
                    'check_interval': 60,   # 1분
                    'alert_threshold': 3    # 3번 연속 실패 시 알림
                }
            ],
            'alerts': {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'sender_email': 'your-email@gmail.com',
                    'sender_password': 'your-password',
                    'recipient_email': 'recipient@example.com'
                },
                'log': {
                    'enabled': True,
                    'file': LOG_FILE
                },
                'console': {
                    'enabled': True
                }
            }
        }
        
        # 기본 설정 저장
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"기본 설정 파일이 생성되었습니다: {CONFIG_FILE}")
        print("설정 파일을 편집한 후 프로그램을 다시 실행하세요.")
        return default_config
    
    # 기존 설정 파일 로드
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def send_email_alert(alert_config, subject, message):
    """
    이메일 알림을 보냅니다.
    """
    if not alert_config.get('enabled', False):
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = alert_config['sender_email']
        msg['To'] = alert_config['recipient_email']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(alert_config['smtp_server'], alert_config['smtp_port'])
        server.starttls()
        server.login(alert_config['sender_email'], alert_config['sender_password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"이메일 알림 전송 실패: {e}")
        return False

def log_alert(alert_config, message):
    """
    로그 파일에 알림을 기록합니다.
    """
    if not alert_config.get('enabled', False):
        return False
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(alert_config.get('file', LOG_FILE), 'a') as f:
            f.write(log_entry)
        
        return True
    except Exception as e:
        print(f"로그 기록 실패: {e}")
        return False

def console_alert(alert_config, message):
    """
    콘솔에 알림을 출력합니다.
    """
    if not alert_config.get('enabled', False):
        return False
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    return True

def send_alert(config, subject, message):
    """
    구성된 모든 알림 채널로 알림을 전송합니다.
    """
    alerts = config.get('alerts', {})
    
    # 이메일 알림
    if 'email' in alerts:
        send_email_alert(alerts['email'], subject, message)
    
    # 로그 알림
    if 'log' in alerts:
        log_alert(alerts['log'], message)
    
    # 콘솔 알림
    if 'console' in alerts:
        console_alert(alerts['console'], message)

def check_monitor(monitor, failures):
    """
    모니터 항목을 확인하고 결과를 반환합니다.
    
    Args:
        monitor (dict): 모니터 설정
        failures (dict): 모니터별 연속 실패 횟수
        
    Returns:
        bool: 성공 여부
    """
    monitor_name = monitor['name']
    monitor_type = monitor['type']
    host = monitor['host']
    
    # 이전 실패 기록이 없으면 초기화
    if monitor_name not in failures:
        failures[monitor_name] = 0
    
    if monitor_type == 'ping':
        count = monitor.get('count', 3)
        timeout = monitor.get('timeout', 2)
        
        try:
            result = ping_host(host, count, timeout)
            success = result['received'] > 0  # 적어도 하나의 패킷이 수신되면 성공
            
            if success:
                if failures[monitor_name] > 0:
                    send_alert(
                        config,
                        f"[복구] {monitor_name}",
                        f"{monitor_name}({host})가 복구되었습니다.\n"
                        f"Ping 응답 시간: {result['avg_time']:.2f}ms"
                    )
                    failures[monitor_name] = 0
                
                return True
            else:
                failures[monitor_name] += 1
                
                if failures[monitor_name] >= monitor.get('alert_threshold', 1):
                    send_alert(
                        config,
                        f"[경고] {monitor_name}",
                        f"{monitor_name}({host})에 연결할 수 없습니다.\n"
                        f"Ping 실패: {failures[monitor_name]}회 연속 실패"
                    )
                
                return False
        except Exception as e:
            failures[monitor_name] += 1
            
            if failures[monitor_name] >= monitor.get('alert_threshold', 1):
                send_alert(
                    config,
                    f"[오류] {monitor_name}",
                    f"{monitor_name}({host}) 모니터링 중 오류가 발생했습니다: {e}"
                )
            
            return False
    
    elif monitor_type == 'port':
        port = monitor.get('port', 80)
        timeout = monitor.get('timeout', 1)
        
        try:
            port_result = scan_port(host, port, timeout)
            success = port_result[1]  # port_result = (port, is_open, service_name, response_time)
            
            if success:
                if failures[monitor_name] > 0:
                    send_alert(
                        config,
                        f"[복구] {monitor_name}",
                        f"{monitor_name}({host}:{port})가 복구되었습니다.\n"
                        f"응답 시간: {port_result[3]:.4f}s"
                    )
                    failures[monitor_name] = 0
                
                return True
            else:
                failures[monitor_name] += 1
                
                if failures[monitor_name] >= monitor.get('alert_threshold', 1):
                    send_alert(
                        config,
                        f"[경고] {monitor_name}",
                        f"{monitor_name}({host}:{port})에 연결할 수 없습니다.\n"
                        f"연결 실패: {failures[monitor_name]}회 연속 실패"
                    )
                
                return False
        except Exception as e:
            failures[monitor_name] += 1
            
            if failures[monitor_name] >= monitor.get('alert_threshold', 1):
                send_alert(
                    config,
                    f"[오류] {monitor_name}",
                    f"{monitor_name}({host}:{port}) 모니터링 중 오류가 발생했습니다: {e}"
                )
            
            return False
    
    else:
        send_alert(
            config,
            f"[설정 오류] {monitor_name}",
            f"지원되지 않는 모니터 타입: {monitor_type}"
        )
        return False

def run_monitor():
    """
    모니터링을 실행합니다.
    """
    global config
    config = load_config()
    
    monitors = config.get('monitors', [])
    if not monitors:
        print("모니터링 항목이 설정되지 않았습니다.")
        return
    
    # 각 모니터별 다음 확인 시간
    next_checks = {}
    # 각 모니터별 연속 실패 횟수
    failures = {}
    
    # 각 모니터의 다음 확인 시간 초기화
    for monitor in monitors:
        next_checks[monitor['name']] = 0
    
    print(f"{len(monitors)}개 모니터 항목에 대한 모니터링을 시작합니다.")
    
    try:
        while True:
            current_time = time.time()
            
            for monitor in monitors:
                name = monitor['name']
                
                # 확인 시간이 되었는지 확인
                if current_time >= next_checks[name]:
                    # 모니터 확인
                    console_alert({'enabled': True}, f"모니터 '{name}' 확인 중...")
                    success = check_monitor(monitor, failures)
                    
                    # 다음 확인 시간 설정
                    check_interval = monitor.get('check_interval', 60)  # 기본값: 60초
                    next_checks[name] = current_time + check_interval
            
            # 잠시 대기
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n모니터링이 중지되었습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Network Monitoring Tool')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    if args.config:
        CONFIG_FILE = args.config
    
    run_monitor()
