import time
import statistics
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from .port_scanner import scan_port_basic, scan_port_nonblocking, get_common_ports


class PortScanBenchmark:
    """포트 스캔 성능 벤치마크 클래스"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_scan_methods(self, host: str, ports: List[int], timeout: float = 1.0, 
                             iterations: int = 3) -> Dict[str, Any]:
        """
        다양한 스캔 방법의 성능 비교 벤치마크
        
        Args:
            host: 대상 호스트
            ports: 테스트할 포트 목록
            timeout: 타임아웃 시간
            iterations: 반복 테스트 횟수
        
        Returns:
            벤치마크 결과 딕셔너리
        """
        print(f"성능 벤치마크 시작: {host} ({len(ports)}개 포트, {iterations}회 반복)")
        
        methods = {
            'basic_blocking': self._test_basic_blocking,
            'advanced_nonblocking': self._test_nonblocking,
            'threaded_basic': self._test_threaded_basic,
            'threaded_advanced': self._test_threaded_advanced
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            print(f"\n{method_name} 테스트 중...")
            method_times = []
            method_success_counts = []
            
            for i in range(iterations):
                start_time = time.time()
                success_count = method_func(host, ports, timeout)
                elapsed_time = time.time() - start_time
                
                method_times.append(elapsed_time)
                method_success_counts.append(success_count)
                print(f"  반복 {i+1}: {elapsed_time:.3f}초, {success_count}개 포트 성공")
            
            results[method_name] = {
                'avg_time': statistics.mean(method_times),
                'min_time': min(method_times),
                'max_time': max(method_times),
                'std_dev': statistics.stdev(method_times) if len(method_times) > 1 else 0,
                'avg_success_count': statistics.mean(method_success_counts),
                'total_ports': len(ports),
                'success_rate': statistics.mean(method_success_counts) / len(ports)
            }
        
        # 성능 비교 분석
        fastest_method = min(results.keys(), key=lambda k: results[k]['avg_time'])
        performance_comparison = self._analyze_performance(results, fastest_method)
        
        return {
            'benchmark_results': results,
            'fastest_method': fastest_method,
            'performance_analysis': performance_comparison,
            'test_config': {
                'host': host,
                'ports_tested': len(ports),
                'timeout': timeout,
                'iterations': iterations
            }
        }
    
    def _test_basic_blocking(self, host: str, ports: List[int], timeout: float) -> int:
        """기본 블로킹 소켓 테스트"""
        success_count = 0
        for port in ports:
            _, is_open, _, _ = scan_port_basic(host, port, timeout)
            if is_open:
                success_count += 1
        return success_count
    
    def _test_nonblocking(self, host: str, ports: List[int], timeout: float) -> int:
        """논블로킹 소켓 테스트"""
        success_count = 0
        for port in ports:
            _, is_open, _, _ = scan_port_nonblocking(host, port, timeout)
            if is_open:
                success_count += 1
        return success_count
    
    def _test_threaded_basic(self, host: str, ports: List[int], timeout: float) -> int:
        """멀티스레드 + 기본 소켓 테스트"""
        success_count = 0
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(
                lambda p: scan_port_basic(host, p, timeout), 
                ports
            ))
        
        for _, is_open, _, _ in results:
            if is_open:
                success_count += 1
        return success_count
    
    def _test_threaded_advanced(self, host: str, ports: List[int], timeout: float) -> int:
        """멀티스레드 + 논블로킹 소켓 테스트"""
        success_count = 0
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(
                lambda p: scan_port_nonblocking(host, p, timeout), 
                ports
            ))
        
        for _, is_open, _, _ in results:
            if is_open:
                success_count += 1
        return success_count
    
    def _analyze_performance(self, results: Dict, fastest_method: str) -> Dict[str, Any]:
        """성능 분석 결과 생성"""
        fastest_time = results[fastest_method]['avg_time']
        analysis = {
            'speed_comparison': {},
            'recommendations': [],
            'efficiency_scores': {}
        }
        
        for method, stats in results.items():
            # 속도 비교 (배수)
            speed_ratio = stats['avg_time'] / fastest_time
            analysis['speed_comparison'][method] = {
                'ratio': speed_ratio,
                'description': f"{speed_ratio:.2f}x {'slower' if speed_ratio > 1 else 'faster'}"
            }
            
            # 효율성 점수 (속도 + 성공률)
            efficiency = (stats['success_rate'] * 100) / stats['avg_time']
            analysis['efficiency_scores'][method] = efficiency
        
        # 추천사항 생성
        if results['threaded_advanced']['avg_time'] < results['basic_blocking']['avg_time']:
            analysis['recommendations'].append(
                "논블로킹 소켓 + 멀티스레딩이 기본 방식보다 빠릅니다."
            )
        
        if results['advanced_nonblocking']['success_rate'] > 0.9:
            analysis['recommendations'].append(
                "논블로킹 소켓이 높은 성공률을 보입니다."
            )
        
        return analysis
    
    def print_benchmark_results(self, benchmark_data: Dict):
        """벤치마크 결과를 보기 좋게 출력"""
        print("\n" + "="*60)
        print("포트 스캔 성능 벤치마크 결과")
        print("="*60)
        
        config = benchmark_data['test_config']
        print(f"테스트 대상: {config['host']}")
        print(f"포트 수: {config['ports_tested']}")
        print(f"타임아웃: {config['timeout']}초")
        print(f"반복 횟수: {config['iterations']}회")
        
        print(f"\n가장 빠른 방법: {benchmark_data['fastest_method']}")
        
        print("\n방법별 성능 결과:")
        print("-" * 60)
        
        results = benchmark_data['benchmark_results']
        for method, stats in results.items():
            print(f"\n{method}:")
            print(f"  평균 시간: {stats['avg_time']:.3f}초")
            print(f"  최소/최대: {stats['min_time']:.3f}초 ~ {stats['max_time']:.3f}초")
            print(f"  표준편차: {stats['std_dev']:.3f}")
            print(f"  성공률: {stats['success_rate']:.1%}")
        
        print(f"\n속도 비교 (기준: {benchmark_data['fastest_method']}):")
        print("-" * 40)
        for method, comparison in benchmark_data['performance_analysis']['speed_comparison'].items():
            print(f"{method}: {comparison['description']}")
        
        print(f"\n효율성 점수 (성공률/시간):")
        print("-" * 30)
        efficiency_scores = benchmark_data['performance_analysis']['efficiency_scores']
        sorted_efficiency = sorted(efficiency_scores.items(), key=lambda x: x[1], reverse=True)
        for method, score in sorted_efficiency:
            print(f"{method}: {score:.2f}")
        
        print(f"\n추천사항:")
        print("-" * 20)
        for rec in benchmark_data['performance_analysis']['recommendations']:
            print(f"• {rec}")


class PerformanceOptimizer:
    """포트 스캔 성능 최적화 도구"""
    
    @staticmethod
    def get_optimal_worker_count(host: str, sample_ports: Optional[List[int]] = None, 
                               max_workers: int = 200) -> int:
        """
        최적의 워커 스레드 수 찾기
        
        Args:
            host: 대상 호스트
            sample_ports: 테스트용 포트 목록 (없으면 일반 포트 사용)
            max_workers: 최대 워커 수
        
        Returns:
            최적의 워커 스레드 수
        """
        if sample_ports is None:
            sample_ports = get_common_ports()[:10]  # 10개 포트로 테스트
        
        print(f"최적 워커 수 탐색 중... (최대 {max_workers})")
        
        worker_counts = [10, 25, 50, 75, 100, 150, 200]
        worker_counts = [w for w in worker_counts if w <= max_workers]
        
        best_time = float('inf')
        best_workers = 50
        
        for workers in worker_counts:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                results = list(executor.map(
                    lambda p: scan_port_basic(host, p, 0.5), 
                    sample_ports
                ))
            
            elapsed = time.time() - start_time
            print(f"  워커 {workers}개: {elapsed:.3f}초")
            
            if elapsed < best_time:
                best_time = elapsed
                best_workers = workers
        
        print(f"최적 워커 수: {best_workers}개 ({best_time:.3f}초)")
        return best_workers
    
    @staticmethod
    def auto_optimize_scan_params(host: str) -> Dict[str, Any]:
        """
        자동으로 최적 스캔 파라미터 찾기
        
        Args:
            host: 대상 호스트
        
        Returns:
            최적화된 파라미터 딕셔너리
        """
        print(f"'{host}'에 대한 최적 스캔 파라미터 탐색 중...")
        
        # 샘플 포트로 테스트
        sample_ports = get_common_ports()[:20]
        
        # 1. 최적 타임아웃 찾기
        timeouts = [0.1, 0.3, 0.5, 1.0, 2.0]
        best_timeout = 0.5
        best_timeout_score = 0
        
        print("\n최적 타임아웃 탐색:")
        for timeout in timeouts:
            start_time = time.time()
            success_count = 0
            
            for port in sample_ports[:5]:  # 5개 포트로 빠른 테스트
                _, is_open, _, _ = scan_port_basic(host, port, timeout)
                if is_open:
                    success_count += 1
            
            elapsed = time.time() - start_time
            score = (success_count / len(sample_ports[:5])) / elapsed  # 성공률/시간
            
            print(f"  타임아웃 {timeout}초: 점수 {score:.3f}")
            
            if score > best_timeout_score:
                best_timeout_score = score
                best_timeout = timeout
        
        # 2. 최적 워커 수 찾기
        best_workers = PerformanceOptimizer.get_optimal_worker_count(host, sample_ports[:10])
        
        # 3. 논블로킹 vs 블로킹 성능 비교
        print("\n블로킹 vs 논블로킹 성능 비교:")
        
        # 블로킹 테스트
        start_time = time.time()
        blocking_success = 0
        for port in sample_ports[:5]:
            _, is_open, _, _ = scan_port_basic(host, port, best_timeout)
            if is_open:
                blocking_success += 1
        blocking_time = time.time() - start_time
        
        # 논블로킹 테스트
        start_time = time.time()
        nonblocking_success = 0
        for port in sample_ports[:5]:
            _, is_open, _, _ = scan_port_nonblocking(host, port, best_timeout)
            if is_open:
                nonblocking_success += 1
        nonblocking_time = time.time() - start_time
        
        use_nonblocking = nonblocking_time < blocking_time
        
        print(f"  블로킹: {blocking_time:.3f}초")
        print(f"  논블로킹: {nonblocking_time:.3f}초")
        print(f"  권장: {'논블로킹' if use_nonblocking else '블로킹'}")
        
        optimal_params = {
            'timeout': best_timeout,
            'max_workers': best_workers,
            'use_advanced_options': use_nonblocking,
            'use_adaptive_timeout': True,  # 항상 권장
            'performance_scores': {
                'timeout_score': best_timeout_score,
                'blocking_time': blocking_time,
                'nonblocking_time': nonblocking_time
            }
        }
        
        print(f"\n최적화된 파라미터:")
        print(f"  타임아웃: {best_timeout}초")
        print(f"  워커 수: {best_workers}개")
        print(f"  고급 옵션: {'사용' if use_nonblocking else '미사용'}")
        print(f"  적응형 타임아웃: 사용")
        
        return optimal_params


def run_performance_benchmark(host: str = "127.0.0.1", port_count: int = 20):
    """성능 벤치마크 실행"""
    benchmark = PortScanBenchmark()
    
    # 테스트할 포트 선택
    if host == "127.0.0.1" or host == "localhost":
        # 로컬호스트의 경우 일반 포트들 사용
        test_ports = get_common_ports()[:port_count]
    else:
        # 외부 호스트의 경우 일반적인 웹/DNS 포트들 사용
        test_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995][:port_count]
    
    # 벤치마크 실행
    results = benchmark.benchmark_scan_methods(host, test_ports, timeout=1.0, iterations=2)
    
    # 결과 출력
    benchmark.print_benchmark_results(results)
    
    return results