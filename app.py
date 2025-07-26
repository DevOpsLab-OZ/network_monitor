#!/usr/bin/env python3
from network_monitor.ping_monitor import ping_host, ping_multiple_hosts
from network_monitor.port_scanner import scan_host, get_common_ports
from network_monitor.dns_lookup import dns_lookup, reverse_dns_lookup
from network_monitor.tcp_server import run_tcp_echo_server
from network_monitor.udp_server import run_udp_echo_server
from network_monitor.file_server import run_file_transfer_server
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
    
    # DNS 조회 명령 설정
    dns_parser = subparsers.add_parser('dns', help='Perform DNS lookups')
    dns_subparsers = dns_parser.add_subparsers(dest='dns_command', help='DNS command to run')
    
    # 정방향 DNS 조회
    lookup_parser = dns_subparsers.add_parser('lookup', help='Lookup DNS records for a domain')
    lookup_parser.add_argument('domain', help='Domain to lookup')
    lookup_parser.add_argument('-t', '--type', default='A', help='Record type (A, AAAA, MX, NS, TXT, SOA, CNAME)')
    lookup_parser.add_argument('--timeout', type=float, default=2.0, help='Timeout in seconds')
    
    # 역방향 DNS 조회
    reverse_parser = dns_subparsers.add_parser('reverse', help='Perform reverse DNS lookup for an IP address')
    reverse_parser.add_argument('ip', help='IP address to lookup')
    reverse_parser.add_argument('--timeout', type=float, default=2.0, help='Timeout in seconds')
    
    # 서버 명령 설정
    server_parser = subparsers.add_parser('server', help='Run various servers')
    server_subparsers = server_parser.add_subparsers(dest='server_command', help='Server type to run')
    
    # TCP 에코 서버
    tcp_parser = server_subparsers.add_parser('tcp-echo', help='Run TCP echo server')
    tcp_parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    tcp_parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    tcp_parser.add_argument('--multi', action='store_true', help='Enable multi-client support')
    
    # UDP 에코 서버
    udp_parser = server_subparsers.add_parser('udp-echo', help='Run UDP echo server')
    udp_parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    udp_parser.add_argument('--port', type=int, default=8081, help='Port to bind to (default: 8081)')
    
    # 파일 전송 서버
    file_parser = server_subparsers.add_parser('file-transfer', help='Run file transfer server')
    file_parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    file_parser.add_argument('--port', type=int, default=8082, help='Port to bind to (default: 8082)')
    file_parser.add_argument('--upload-dir', default='uploads', help='Directory to store uploaded files (default: uploads)')
    
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
    
    elif args.command == 'dns':
        if args.dns_command == 'lookup':
            result = dns_lookup(args.domain, args.type, args.timeout)
            
            print(f"\nDNS Lookup Results for {result['domain']} ({result['record_type']} records):")
            
            if result['success']:
                print(f"Found {result['record_count']} records in {result['response_time']:.4f} seconds")
                
                if result['record_type'] == 'A' or result['record_type'] == 'AAAA':
                    print("\nIP Addresses:")
                    for record in result['records']:
                        print(f"  {record['value']} (TTL: {record['ttl']}s)")
                        
                elif result['record_type'] == 'MX':
                    print("\nMail Servers:")
                    # 우선순위에 따라 정렬
                    for record in sorted(result['records'], key=lambda x: x['preference']):
                        print(f"  {record['value']} (Preference: {record['preference']}, TTL: {record['ttl']}s)")
                        
                elif result['record_type'] == 'NS':
                    print("\nName Servers:")
                    for record in result['records']:
                        print(f"  {record['value']} (TTL: {record['ttl']}s)")
                        
                elif result['record_type'] == 'TXT':
                    print("\nTXT Records:")
                    for record in result['records']:
                        print(f"  {record['value']} (TTL: {record['ttl']}s)")
                        
                elif result['record_type'] == 'SOA':
                    print("\nSOA Record:")
                    for record in result['records']:
                        print(f"  Primary NS: {record['mname']}")
                        print(f"  Email: {record['rname']}")
                        print(f"  Serial: {record['serial']}")
                        print(f"  Refresh: {record['refresh']}s")
                        print(f"  Retry: {record['retry']}s")
                        print(f"  Expire: {record['expire']}s")
                        print(f"  Minimum TTL: {record['minimum']}s")
                        print(f"  TTL: {record['ttl']}s")
                        
                elif result['record_type'] == 'CNAME':
                    print("\nCanonical Names:")
                    for record in result['records']:
                        print(f"  {record['value']} (TTL: {record['ttl']}s)")
                        
                else:
                    print("\nRecords:")
                    for record in result['records']:
                        print(f"  {record['value']} (TTL: {record['ttl']}s)")
            else:
                print(f"Error: {result['error']}")
                
        elif args.dns_command == 'reverse':
            result = reverse_dns_lookup(args.ip, args.timeout)
            
            print(f"\nReverse DNS Lookup Results for {result['ip_address']}:")
            
            if result['success']:
                print(f"Found hostname in {result['response_time']:.4f} seconds")
                print(f"Hostname: {result['hostname']}")
                
                if result['aliases'] and len(result['aliases']) > 0:
                    print("Aliases:")
                    for alias in result['aliases']:
                        print(f"  {alias}")
            else:
                print(f"Error: {result['error']}")
                
        else:
            dns_parser.print_help()
    
    elif args.command == 'server':
        if args.server_command == 'tcp-echo':
            print(f"Starting TCP Echo Server on {args.host}:{args.port}")
            if args.multi:
                print("Multi-client mode enabled")
            run_tcp_echo_server(args.host, args.port, args.multi)
            
        elif args.server_command == 'udp-echo':
            print(f"Starting UDP Echo Server on {args.host}:{args.port}")
            run_udp_echo_server(args.host, args.port)
            
        elif args.server_command == 'file-transfer':
            print(f"Starting File Transfer Server on {args.host}:{args.port}")
            print(f"Upload directory: {args.upload_dir}")
            run_file_transfer_server(args.host, args.port, args.upload_dir)
            
        else:
            server_parser.print_help()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
