import dns.resolver
import socket
import time
from .config import DEFAULT_TIMEOUT

def dns_lookup(domain, record_type='A', timeout=DEFAULT_TIMEOUT):
    """
    지정된 도메인에 대한 DNS 레코드를 조회합니다.
    
    Args:
        domain (str): 조회할 도메인 이름
        record_type (str): 조회할 DNS 레코드 유형 (A, AAAA, MX, NS, TXT, SOA, CNAME 등)
        timeout (float): 조회 타임아웃 시간(초)
        
    Returns:
        dict: DNS 조회 결과를 포함하는 딕셔너리
    """
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout
    
    results = []
    
    try:
        start_time = time.time()
        answers = resolver.resolve(domain, record_type)
        response_time = time.time() - start_time
        
        for rdata in answers:
            if record_type == 'A' or record_type == 'AAAA':
                results.append({
                    'value': str(rdata.address),
                    'ttl': answers.rrset.ttl
                })
            elif record_type == 'MX':
                results.append({
                    'value': str(rdata.exchange),
                    'preference': rdata.preference,
                    'ttl': answers.rrset.ttl
                })
            elif record_type == 'NS':
                results.append({
                    'value': str(rdata.target),
                    'ttl': answers.rrset.ttl
                })
            elif record_type == 'TXT':
                results.append({
                    'value': str(rdata.strings),
                    'ttl': answers.rrset.ttl
                })
            elif record_type == 'SOA':
                results.append({
                    'mname': str(rdata.mname),
                    'rname': str(rdata.rname),
                    'serial': rdata.serial,
                    'refresh': rdata.refresh,
                    'retry': rdata.retry,
                    'expire': rdata.expire,
                    'minimum': rdata.minimum,
                    'ttl': answers.rrset.ttl
                })
            elif record_type == 'CNAME':
                results.append({
                    'value': str(rdata.target),
                    'ttl': answers.rrset.ttl
                })
            else:
                results.append({
                    'value': str(rdata),
                    'ttl': answers.rrset.ttl
                })
        
        return {
            'domain': domain,
            'record_type': record_type,
            'records': results,
            'record_count': len(results),
            'response_time': response_time,
            'success': True,
            'error': None
        }
    
    except dns.resolver.NXDOMAIN:
        return {
            'domain': domain,
            'record_type': record_type,
            'records': [],
            'record_count': 0,
            'response_time': None,
            'success': False,
            'error': 'Domain does not exist'
        }
    except dns.resolver.NoAnswer:
        return {
            'domain': domain,
            'record_type': record_type,
            'records': [],
            'record_count': 0,
            'response_time': None,
            'success': False,
            'error': f'No {record_type} records found'
        }
    except dns.resolver.Timeout:
        return {
            'domain': domain,
            'record_type': record_type,
            'records': [],
            'record_count': 0,
            'response_time': None,
            'success': False,
            'error': 'DNS query timed out'
        }
    except Exception as e:
        return {
            'domain': domain,
            'record_type': record_type,
            'records': [],
            'record_count': 0,
            'response_time': None,
            'success': False,
            'error': str(e)
        }

def reverse_dns_lookup(ip_address, timeout=DEFAULT_TIMEOUT):
    """
    IP 주소에 대한 역방향 DNS 조회를 수행합니다.
    
    Args:
        ip_address (str): 조회할 IP 주소
        timeout (float): 조회 타임아웃 시간(초)
        
    Returns:
        dict: 역방향 DNS 조회 결과를 포함하는 딕셔너리
    """
    try:
        start_time = time.time()
        hostname = socket.gethostbyaddr(ip_address)
        response_time = time.time() - start_time
        
        return {
            'ip_address': ip_address,
            'hostname': hostname[0],
            'aliases': hostname[1],
            'response_time': response_time,
            'success': True,
            'error': None
        }
    except socket.herror:
        return {
            'ip_address': ip_address,
            'hostname': None,
            'aliases': None,
            'response_time': None,
            'success': False,
            'error': 'No hostname found for IP address'
        }
    except socket.timeout:
        return {
            'ip_address': ip_address,
            'hostname': None,
            'aliases': None,
            'response_time': None,
            'success': False,
            'error': 'Lookup timed out'
        }
    except Exception as e:
        return {
            'ip_address': ip_address,
            'hostname': None,
            'aliases': None,
            'response_time': None,
            'success': False,
            'error': str(e)
        }
