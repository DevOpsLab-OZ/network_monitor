#!/usr/bin/env python3
from network_monitor.ping_monitor import ping_host, ping_multiple_hosts
import argparse

def main():
    parser = argparse.ArgumentParser(description='Network Monitoring Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Ping 명령 설정
    ping_parser = subparsers.add_parser('ping', help='Ping a host')
    ping_parser.add_argument('host', help='Host to ping')
    ping_parser.add_argument('-c', '--count', type=int, default=5, help='Number of packets to send')
    ping_parser.add_argument('-t', '--timeout', type=int, default=2, help='Timeout in seconds')
    
    # TODO: 다른 명령들 추가 (port-scan, dns-lookup 등)
    
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
    # TODO: 다른 명령들 처리
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
