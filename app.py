#!/usr/bin/env python3
from network_monitor.ping_monitor import ping_host, ping_multiple_hosts
from network_monitor.port_scanner import scan_host, get_common_ports
import argparse

def main():
    parser = argparse.ArgumentParser(description='Network Monitoring Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Ping 명령 설정
    ping_parser = subparsers.add_parser('ping', help='Ping a host')
    ping_parser.add_argument('host', help='Host to ping')
    ping_parser.add_argument('-c', '--count', type=int, default=5, help='Number of packets to send')
    ping_parser.add_argument('-t', '--timeout', type=int, default=2, help='Timeout in seconds')
    
    # 포트 스캔 명령 설정
    scan_parser = subparsers.add_parser('scan', help='Scan ports on a host')
    scan_parser.add_argument('host', help='Host to scan')
    scan_parser.add_argument('-p', '--ports', help='Port range to scan (e.g. 1-1024)')
    scan_parser.add_argument('--common', action='store_true', help='Scan only common ports')
    scan_parser.add_argument('-t', '--timeout', type=float, default=0.5, help='Timeout in seconds for each port')
    
    args = parser.parse_args()
    
    if args.command == 'ping':
        result = ping_host(args.host, args.count, args.timeout)
        print("\nPing Statistics:")
        print(f"Host: {result['host']}")
        print(f"Packets: Transmitted = {result['transmitted']}, Received = {result['received']}, "
              f"Lost = {result['packet_loss']} ({result['packet_loss_percent']:.1f}% loss)")
        
        if result['avg_time'] is not None:
            print(f"Approximate round trip times in milliseconds:")
            print(f"Minimum = {result['min_time']:.2f}ms, Maximum = {result['max_time']:.2f}ms, "
                  f"Average = {result['avg_time']:.2f}ms")
    
    elif args.command == 'scan':
        # 포트 범위 결정
        if args.common:
            # 일반적인 포트만 스캔
            common_ports = get_common_ports()
            print(f"Scanning {len(common_ports)} common ports...")
            
            # 각 포트 개별적으로 스캔
            results = []
            for port in common_ports:
                port_result = scan_host(args.host, (port, port), args.timeout)
                if port_result['open_ports']:
                    results.extend(port_result['open_ports'])
            
            print("\nScan Results:")
            print(f"Host: {args.host}")
            print(f"Open ports: {len(results)}/{len(common_ports)}")
            
            if results:
                print("\nOpen Ports:")
                for port_info in sorted(results, key=lambda x: x['port']):
                    print(f"  {port_info['port']}/tcp - {port_info['service']} "
                          f"({port_info['response_time']:.4f}s)")
            
        elif args.ports:
            # 지정된 포트 범위 스캔
            try:
                start_port, end_port = map(int, args.ports.split('-'))
                if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                    raise ValueError("Port numbers must be between 1 and 65535")
            except ValueError:
                print("Invalid port range. Format should be: start-end (e.g. 1-1024)")
                return
            
            result = scan_host(args.host, (start_port, end_port), args.timeout)
            
            print("\nScan Results:")
            print(f"Host: {result['host']}")
            print(f"Port range: {result['start_port']}-{result['end_port']}")
            print(f"Open ports: {result['open_port_count']}/{result['total_ports_scanned']}")
            print(f"Scan completed in {result['scan_time']:.2f} seconds")
            
            if result['open_ports']:
                print("\nOpen Ports:")
                for port_info in sorted(result['open_ports'], key=lambda x: x['port']):
                    print(f"  {port_info['port']}/tcp - {port_info['service']} "
                          f"({port_info['response_time']:.4f}s)")
        else:
            # 기본 포트 범위(1-1024) 사용
            result = scan_host(args.host)
            
            print("\nScan Results:")
            print(f"Host: {result['host']}")
            print(f"Port range: {result['start_port']}-{result['end_port']}")
            print(f"Open ports: {result['open_port_count']}/{result['total_ports_scanned']}")
            print(f"Scan completed in {result['scan_time']:.2f} seconds")
            
            if result['open_ports']:
                print("\nOpen Ports:")
                for port_info in sorted(result['open_ports'], key=lambda x: x['port']):
                    print(f"  {port_info['port']}/tcp - {port_info['service']} "
                          f"({port_info['response_time']:.4f}s)")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
