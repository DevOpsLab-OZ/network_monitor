from flask import Flask, render_template, request, jsonify
from network_monitor.ping_monitor import ping_host
from network_monitor.port_scanner import scan_host, get_common_ports
from network_monitor.dns_lookup import dns_lookup, reverse_dns_lookup
from network_monitor.performance_optimizer import PerformanceOptimizer, run_performance_benchmark
import socket
import os

app = Flask(__name__)

# 템플릿 디렉토리가 없으면 생성
os.makedirs('templates', exist_ok=True)

# 기본 HTML 템플릿 생성
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Monitoring Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .tool-section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select {
            margin-bottom: 15px;
            padding: 8px;
            width: 100%;
            box-sizing: border-box;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            border-radius: 3px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 3px;
            white-space: pre-wrap;
            display: none;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
            text-align: left;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Network Monitoring Tool</h1>
        
        <div class="tool-section">
            <h2>Ping Test</h2>
            <form id="pingForm">
                <label for="pingHost">Host:</label>
                <input type="text" id="pingHost" name="host" placeholder="e.g., google.com or 8.8.8.8" required>
                
                <label for="pingCount">Count:</label>
                <input type="number" id="pingCount" name="count" value="5" min="1" max="20">
                
                <label for="pingTimeout">Timeout (seconds):</label>
                <input type="number" id="pingTimeout" name="timeout" value="2" min="1" max="10" step="0.5">
                
                <button type="submit">Run Ping Test</button>
            </form>
            <div class="loading" id="pingLoading">Running ping test...</div>
            <div class="result" id="pingResult"></div>
        </div>
        
        <div class="tool-section">
            <h2>Port Scanner</h2>
            <form id="scanForm">
                <label for="scanHost">Host:</label>
                <input type="text" id="scanHost" name="host" placeholder="e.g., google.com or 8.8.8.8" required>
                
                <label for="scanType">Scan Type:</label>
                <select id="scanType" name="scanType">
                    <option value="range">Port Range</option>
                    <option value="common">Common Ports</option>
                </select>
                
                <div id="portRangeGroup">
                    <label for="startPort">Start Port:</label>
                    <input type="number" id="startPort" name="startPort" value="1" min="1" max="65535">
                    
                    <label for="endPort">End Port:</label>
                    <input type="number" id="endPort" name="endPort" value="1024" min="1" max="65535">
                </div>
                
                <label for="scanTimeout">Timeout (seconds):</label>
                <input type="number" id="scanTimeout" name="timeout" value="0.5" min="0.1" max="5" step="0.1">
                
                <h3>Advanced Options</h3>
                <div style="margin-bottom: 15px;">
                    <label style="display: inline-block; margin-right: 20px;">
                        <input type="checkbox" id="advancedOptions" name="advanced" style="width: auto; margin-right: 5px;">
                        Use Advanced Socket Options (Non-blocking)
                    </label>
                    <label style="display: inline-block; margin-right: 20px;">
                        <input type="checkbox" id="adaptiveTimeout" name="adaptiveTimeout" style="width: auto; margin-right: 5px;">
                        Adaptive Timeout
                    </label>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <button type="submit" style="margin-right: 10px;">Scan Ports</button>
                    <button type="button" id="optimizeBtn" style="background-color: #e67e22; margin-right: 10px;">Auto Optimize</button>
                    <button type="button" id="benchmarkBtn" style="background-color: #9b59b6;">Benchmark</button>
                </div>
            </form>
            <div class="loading" id="scanLoading">Scanning ports...</div>
            <div class="result" id="scanResult"></div>
        </div>
        
        <div class="tool-section">
            <h2>DNS Lookup</h2>
            <form id="dnsForm">
                <label for="dnsType">Lookup Type:</label>
                <select id="dnsType" name="dnsType">
                    <option value="forward">Forward Lookup</option>
                    <option value="reverse">Reverse Lookup</option>
                </select>
                
                <div id="forwardLookupGroup">
                    <label for="dnsDomain">Domain:</label>
                    <input type="text" id="dnsDomain" name="domain" placeholder="e.g., google.com" required>
                    
                    <label for="recordType">Record Type:</label>
                    <select id="recordType" name="recordType">
                        <option value="A">A (IPv4 Address)</option>
                        <option value="AAAA">AAAA (IPv6 Address)</option>
                        <option value="MX">MX (Mail Exchange)</option>
                        <option value="NS">NS (Name Server)</option>
                        <option value="TXT">TXT (Text)</option>
                        <option value="SOA">SOA (Start of Authority)</option>
                        <option value="CNAME">CNAME (Canonical Name)</option>
                    </select>
                </div>
                
                <div id="reverseLookupGroup" style="display: none;">
                    <label for="dnsIp">IP Address:</label>
                    <input type="text" id="dnsIp" name="ip" placeholder="e.g., 8.8.8.8">
                </div>
                
                <label for="dnsTimeout">Timeout (seconds):</label>
                <input type="number" id="dnsTimeout" name="timeout" value="2" min="0.5" max="10" step="0.5">
                
                <button type="submit">Lookup</button>
            </form>
            <div class="loading" id="dnsLoading">Performing DNS lookup...</div>
            <div class="result" id="dnsResult"></div>
        </div>
        
        <div class="tool-section">
            <h2>Server Status</h2>
            <p>Monitor running Docker services and system status</p>
            <button id="checkServersBtn" style="margin-bottom: 15px;">Check Server Status</button>
            <div class="loading" id="serverLoading" style="display: none;">Checking server status...</div>
            <div class="result" id="serverResult"></div>
        </div>
        
        <div class="tool-section">
            <h2>Monitoring Configuration</h2>
            <p>View current monitoring settings and status</p>
            <button id="checkMonitoringBtn" style="margin-bottom: 15px;">Check Monitoring Config</button>
            <div class="loading" id="monitoringLoading" style="display: none;">Loading monitoring configuration...</div>
            <div class="result" id="monitoringResult"></div>
        </div>
    </div>
    
    <script>
        // Toggle forward/reverse lookup forms
        document.getElementById('dnsType').addEventListener('change', function() {
            if (this.value === 'forward') {
                document.getElementById('forwardLookupGroup').style.display = 'block';
                document.getElementById('reverseLookupGroup').style.display = 'none';
                document.getElementById('dnsDomain').required = true;
                document.getElementById('dnsIp').required = false;
            } else {
                document.getElementById('forwardLookupGroup').style.display = 'none';
                document.getElementById('reverseLookupGroup').style.display = 'block';
                document.getElementById('dnsDomain').required = false;
                document.getElementById('dnsIp').required = true;
            }
        });
        
        // Toggle port range input
        document.getElementById('scanType').addEventListener('change', function() {
            if (this.value === 'range') {
                document.getElementById('portRangeGroup').style.display = 'block';
            } else {
                document.getElementById('portRangeGroup').style.display = 'none';
            }
        });
        
        // Ping form submission
        document.getElementById('pingForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const host = document.getElementById('pingHost').value;
            const count = document.getElementById('pingCount').value;
            const timeout = document.getElementById('pingTimeout').value;
            
            document.getElementById('pingResult').style.display = 'none';
            document.getElementById('pingLoading').style.display = 'block';
            
            fetch('/api/ping', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    host: host,
                    count: parseInt(count),
                    timeout: parseFloat(timeout)
                }),
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('pingResult');
                
                if (data.success) {
                    let output = `Host: ${data.host}\\n`;
                    output += `Packets: Transmitted = ${data.transmitted}, Received = ${data.received}, `;
                    output += `Lost = ${data.packet_loss} (${data.packet_loss_percent.toFixed(1)}% loss)\\n\\n`;
                    
                    if (data.avg_time !== null) {
                        output += `Approximate round trip times in milliseconds:\\n`;
                        output += `Minimum = ${data.min_time.toFixed(2)}ms, Maximum = ${data.max_time.toFixed(2)}ms, `;
                        output += `Average = ${data.avg_time.toFixed(2)}ms\\n\\n`;
                    }
                    
                    output += `Detailed Results:\\n`;
                    data.results.forEach((result, i) => {
                        if (result.success) {
                            output += `Ping ${i+1}: Success (${result.time.toFixed(2)} ms)\\n`;
                        } else {
                            output += `Ping ${i+1}: Failed (${result.error})\\n`;
                        }
                    });
                    
                    resultDiv.innerHTML = output;
                    resultDiv.classList.remove('error');
                } else {
                    resultDiv.innerHTML = `Error: ${data.error}`;
                    resultDiv.classList.add('error');
                }
                
                resultDiv.style.display = 'block';
                document.getElementById('pingLoading').style.display = 'none';
            })
            .catch(error => {
                const resultDiv = document.getElementById('pingResult');
                resultDiv.innerHTML = `Error: ${error.message}`;
                resultDiv.classList.add('error');
                resultDiv.style.display = 'block';
                document.getElementById('pingLoading').style.display = 'none';
            });
        });
        
        // Port scan form submission
        document.getElementById('scanForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const host = document.getElementById('scanHost').value;
            const scanType = document.getElementById('scanType').value;
            const startPort = document.getElementById('startPort').value;
            const endPort = document.getElementById('endPort').value;
            const timeout = document.getElementById('scanTimeout').value;
            const advanced = document.getElementById('advancedOptions').checked;
            const adaptiveTimeout = document.getElementById('adaptiveTimeout').checked;
            
            document.getElementById('scanResult').style.display = 'none';
            document.getElementById('scanLoading').style.display = 'block';
            
            let requestData = {
                host: host,
                scan_type: scanType,
                timeout: parseFloat(timeout),
                advanced: advanced,
                adaptive_timeout: adaptiveTimeout
            };
            
            if (scanType === 'range') {
                requestData.start_port = parseInt(startPort);
                requestData.end_port = parseInt(endPort);
            }
            
            fetch('/api/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('scanResult');
                
                if (data.success) {
                    let output = `Host: ${data.host}\\n`;
                    
                    if (scanType === 'range') {
                        output += `Port range: ${data.start_port}-${data.end_port}\\n`;
                    } else {
                        output += `Scan type: Common ports\\n`;
                    }
                    
                    output += `Open ports: ${data.open_ports.length}/${data.total_ports_scanned}\\n`;
                    output += `Scan completed in ${data.scan_time.toFixed(2)} seconds\\n`;
                    
                    if (data.scan_method) {
                        output += `Scan method: ${data.scan_method}\\n`;
                    }
                    
                    if (data.timeout_stats) {
                        output += `Adaptive timeout stats:\\n`;
                        output += `  - Average response: ${data.timeout_stats.avg_response_time.toFixed(3)}s\\n`;
                        output += `  - Success rate: ${(data.timeout_stats.success_rate * 100).toFixed(1)}%\\n`;
                        output += `  - Final timeout: ${data.timeout_stats.current_timeout.toFixed(3)}s\\n`;
                    }
                    
                    output += `\\n`;
                    
                    if (data.open_ports.length > 0) {
                        output += `Open Ports:\\n`;
                        
                        // Generate a table for open ports
                        let table = '<table><tr><th>Port</th><th>Service</th><th>Response Time</th></tr>';
                        
                        data.open_ports.sort((a, b) => a.port - b.port).forEach(port => {
                            table += `<tr><td>${port.port}/tcp</td><td>${port.service}</td><td>${port.response_time.toFixed(4)}s</td></tr>`;
                        });
                        
                        table += '</table>';
                        
                        output += table;
                    } else {
                        output += `No open ports found.`;
                    }
                    
                    resultDiv.innerHTML = output;
                    resultDiv.classList.remove('error');
                } else {
                    resultDiv.innerHTML = `Error: ${data.error}`;
                    resultDiv.classList.add('error');
                }
                
                resultDiv.style.display = 'block';
                document.getElementById('scanLoading').style.display = 'none';
            })
            .catch(error => {
                const resultDiv = document.getElementById('scanResult');
                resultDiv.innerHTML = `Error: ${error.message}`;
                resultDiv.classList.add('error');
                resultDiv.style.display = 'block';
                document.getElementById('scanLoading').style.display = 'none';
            });
        });
        
        // Auto Optimize button
        document.getElementById('optimizeBtn').addEventListener('click', function() {
            const host = document.getElementById('scanHost').value;
            if (!host) {
                alert('Please enter a host to optimize for');
                return;
            }
            
            document.getElementById('scanResult').style.display = 'none';
            document.getElementById('scanLoading').innerHTML = 'Auto-optimizing scan parameters...';
            document.getElementById('scanLoading').style.display = 'block';
            
            fetch('/api/optimize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ host: host }),
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('scanResult');
                
                if (data.success) {
                    let output = `Auto-Optimization Results for ${data.host}:\\n\\n`;
                    output += `Optimized Parameters:\\n`;
                    output += `  - Timeout: ${data.optimal_params.timeout}s\\n`;
                    output += `  - Workers: ${data.optimal_params.max_workers}\\n`;
                    output += `  - Advanced Options: ${data.optimal_params.use_advanced_options ? 'Enabled' : 'Disabled'}\\n`;
                    output += `  - Adaptive Timeout: ${data.optimal_params.use_adaptive_timeout ? 'Enabled' : 'Disabled'}\\n\\n`;
                    
                    output += `Scan Results:\\n`;
                    output += `Host: ${data.scan_result.host}\\n`;
                    output += `Open ports: ${data.scan_result.open_port_count}/${data.scan_result.total_ports_scanned}\\n`;
                    output += `Scan time: ${data.scan_result.scan_time.toFixed(2)}s\\n`;
                    output += `Method: ${data.scan_result.scan_method}\\n\\n`;
                    
                    if (data.scan_result.open_ports && data.scan_result.open_ports.length > 0) {
                        output += `Open Ports:\\n`;
                        let table = '<table><tr><th>Port</th><th>Service</th><th>Response Time</th></tr>';
                        data.scan_result.open_ports.sort((a, b) => a.port - b.port).forEach(port => {
                            table += `<tr><td>${port.port}/tcp</td><td>${port.service}</td><td>${port.response_time.toFixed(4)}s</td></tr>`;
                        });
                        table += '</table>';
                        output += table;
                    }
                    
                    resultDiv.innerHTML = output;
                    resultDiv.classList.remove('error');
                } else {
                    resultDiv.innerHTML = `Error: ${data.error}`;
                    resultDiv.classList.add('error');
                }
                
                resultDiv.style.display = 'block';
                document.getElementById('scanLoading').style.display = 'none';
                document.getElementById('scanLoading').innerHTML = 'Scanning ports...';
            })
            .catch(error => {
                const resultDiv = document.getElementById('scanResult');
                resultDiv.innerHTML = `Error: ${error.message}`;
                resultDiv.classList.add('error');
                resultDiv.style.display = 'block';
                document.getElementById('scanLoading').style.display = 'none';
                document.getElementById('scanLoading').innerHTML = 'Scanning ports...';
            });
        });
        
        // Benchmark button
        document.getElementById('benchmarkBtn').addEventListener('click', function() {
            const host = document.getElementById('scanHost').value;
            if (!host) {
                alert('Please enter a host to benchmark');
                return;
            }
            
            document.getElementById('scanResult').style.display = 'none';
            document.getElementById('scanLoading').innerHTML = 'Running performance benchmark...';
            document.getElementById('scanLoading').style.display = 'block';
            
            fetch('/api/benchmark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ host: host }),
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('scanResult');
                
                if (data.success) {
                    let output = `Performance Benchmark Results\\n`;
                    output += `${'='.repeat(60)}\\n`;
                    output += `Test Target: ${data.test_config.host}\\n`;
                    output += `Ports Tested: ${data.test_config.ports_tested}\\n`;
                    output += `Timeout: ${data.test_config.timeout}s\\n`;
                    output += `Iterations: ${data.test_config.iterations}\\n\\n`;
                    
                    output += `Fastest Method: ${data.fastest_method}\\n\\n`;
                    
                    output += `Method Performance Results:\\n`;
                    output += `${'-'.repeat(60)}\\n`;
                    
                    for (const [method, stats] of Object.entries(data.benchmark_results)) {
                        output += `\\n${method}:\\n`;
                        output += `  Average time: ${stats.avg_time.toFixed(3)}s\\n`;
                        output += `  Min/Max: ${stats.min_time.toFixed(3)}s ~ ${stats.max_time.toFixed(3)}s\\n`;
                        output += `  Success rate: ${(stats.success_rate * 100).toFixed(1)}%\\n`;
                    }
                    
                    output += `\\nSpeed Comparison (vs ${data.fastest_method}):\\n`;
                    output += `${'-'.repeat(40)}\\n`;
                    for (const [method, comparison] of Object.entries(data.performance_analysis.speed_comparison)) {
                        output += `${method}: ${comparison.description}\\n`;
                    }
                    
                    if (data.performance_analysis.recommendations.length > 0) {
                        output += `\\nRecommendations:\\n`;
                        output += `${'-'.repeat(20)}\\n`;
                        data.performance_analysis.recommendations.forEach(rec => {
                            output += `• ${rec}\\n`;
                        });
                    }
                    
                    resultDiv.innerHTML = output;
                    resultDiv.classList.remove('error');
                } else {
                    resultDiv.innerHTML = `Error: ${data.error}`;
                    resultDiv.classList.add('error');
                }
                
                resultDiv.style.display = 'block';
                document.getElementById('scanLoading').style.display = 'none';
                document.getElementById('scanLoading').innerHTML = 'Scanning ports...';
            })
            .catch(error => {
                const resultDiv = document.getElementById('scanResult');
                resultDiv.innerHTML = `Error: ${error.message}`;
                resultDiv.classList.add('error');
                resultDiv.style.display = 'block';
                document.getElementById('scanLoading').style.display = 'none';
                document.getElementById('scanLoading').innerHTML = 'Scanning ports...';
            });
        });
        
        // Server status check
        document.getElementById('checkServersBtn').addEventListener('click', function() {
            document.getElementById('serverResult').style.display = 'none';
            document.getElementById('serverLoading').style.display = 'block';
            
            fetch('/api/server-status', {
                method: 'GET',
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('serverResult');
                
                if (data.success) {
                    let output = `Server Status Report\\n`;
                    output += `${'='.repeat(50)}\\n`;
                    output += `Check Time: ${data.check_time}\\n\\n`;
                    
                    if (data.docker_services && data.docker_services.length > 0) {
                        output += `Docker Services:\\n`;
                        output += `${'-'.repeat(30)}\\n`;
                        
                        let table = '<table><tr><th>Service</th><th>Status</th><th>Port</th><th>Response</th></tr>';
                        
                        data.docker_services.forEach(service => {
                            const statusColor = service.accessible ? 'green' : 'red';
                            table += `<tr>`;
                            table += `<td>${service.name}</td>`;
                            table += `<td style="color: ${statusColor};">${service.accessible ? 'Running' : 'Down'}</td>`;
                            table += `<td>${service.port}</td>`;
                            table += `<td>${service.response_time ? service.response_time.toFixed(3) + 's' : 'N/A'}</td>`;
                            table += `</tr>`;
                        });
                        table += '</table>';
                        
                        output += table;
                    } else {
                        output += `No Docker services detected.\\n`;
                    }
                    
                    output += `\\n\\nSystem Info:\\n`;
                    output += `${'-'.repeat(20)}\\n`;
                    output += `Web Server: Running (Port 5000)\\n`;
                    output += `Network Monitor: Active\\n`;
                    
                    resultDiv.innerHTML = output;
                    resultDiv.classList.remove('error');
                } else {
                    resultDiv.innerHTML = `Error: ${data.error}`;
                    resultDiv.classList.add('error');
                }
                
                resultDiv.style.display = 'block';
                document.getElementById('serverLoading').style.display = 'none';
            })
            .catch(error => {
                const resultDiv = document.getElementById('serverResult');
                resultDiv.innerHTML = `Error: ${error.message}`;
                resultDiv.classList.add('error');
                resultDiv.style.display = 'block';
                document.getElementById('serverLoading').style.display = 'none';
            });
        });
        
        // Monitoring configuration check
        document.getElementById('checkMonitoringBtn').addEventListener('click', function() {
            document.getElementById('monitoringResult').style.display = 'none';
            document.getElementById('monitoringLoading').style.display = 'block';
            
            fetch('/api/monitoring-config', {
                method: 'GET',
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('monitoringResult');
                
                if (data.success) {
                    let output = `Monitoring Configuration\\n`;
                    output += `${'='.repeat(50)}\\n`;
                    output += `Config File: ${data.config_file}\\n`;
                    output += `File Exists: ${data.config_exists ? 'Yes' : 'No'}\\n\\n`;
                    
                    if (data.config_exists && data.monitors) {
                        output += `Configured Monitors:\\n`;
                        output += `${'-'.repeat(30)}\\n`;
                        
                        let table = '<table><tr><th>Name</th><th>Type</th><th>Target</th><th>Interval</th><th>Threshold</th></tr>';
                        
                        data.monitors.forEach(monitor => {
                            table += `<tr>`;
                            table += `<td>${monitor.name}</td>`;
                            table += `<td>${monitor.type}</td>`;
                            table += `<td>${monitor.host}${monitor.port ? ':' + monitor.port : ''}</td>`;
                            table += `<td>${monitor.check_interval}s</td>`;
                            table += `<td>${monitor.alert_threshold}</td>`;
                            table += `</tr>`;
                        });
                        table += '</table>';
                        
                        output += table;
                        
                        output += `\\n\\nAlert Settings:\\n`;
                        output += `${'-'.repeat(20)}\\n`;
                        if (data.alerts) {
                            if (data.alerts.email && data.alerts.email.enabled) {
                                output += `Email: Enabled (${data.alerts.email.recipient_email})\\n`;
                            }
                            if (data.alerts.log && data.alerts.log.enabled) {
                                output += `Log File: Enabled (${data.alerts.log.file})\\n`;
                            }
                            if (data.alerts.console && data.alerts.console.enabled) {
                                output += `Console: Enabled\\n`;
                            }
                        }
                    } else {
                        output += `No monitoring configuration found.\\n`;
                        output += `Run 'python monitor.py' to create default config.\\n`;
                    }
                    
                    output += `\\n\\nTo edit configuration:\\n`;
                    output += `1. Edit monitor_config.yaml file\\n`;
                    output += `2. Restart monitoring service\\n`;
                    
                    resultDiv.innerHTML = output;
                    resultDiv.classList.remove('error');
                } else {
                    resultDiv.innerHTML = `Error: ${data.error}`;
                    resultDiv.classList.add('error');
                }
                
                resultDiv.style.display = 'block';
                document.getElementById('monitoringLoading').style.display = 'none';
            })
            .catch(error => {
                const resultDiv = document.getElementById('monitoringResult');
                resultDiv.innerHTML = `Error: ${error.message}`;
                resultDiv.classList.add('error');
                resultDiv.style.display = 'block';
                document.getElementById('monitoringLoading').style.display = 'none';
            });
        });
        
        // DNS lookup form submission
        document.getElementById('dnsForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const lookupType = document.getElementById('dnsType').value;
            const timeout = document.getElementById('dnsTimeout').value;
            
            let requestData = {
                lookup_type: lookupType,
                timeout: parseFloat(timeout)
            };
            
            if (lookupType === 'forward') {
                requestData.domain = document.getElementById('dnsDomain').value;
                requestData.record_type = document.getElementById('recordType').value;
            } else {
                requestData.ip = document.getElementById('dnsIp').value;
            }
            
            document.getElementById('dnsResult').style.display = 'none';
            document.getElementById('dnsLoading').style.display = 'block';
            
            fetch('/api/dns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('dnsResult');
                
                if (data.success) {
                    let output = '';
                    
                    if (lookupType === 'forward') {
                        output = `DNS Lookup Results for ${data.domain} (${data.record_type} records):\\n`;
                        output += `Found ${data.record_count} records in ${data.response_time.toFixed(4)} seconds\\n\\n`;
                        
                        if (data.record_count > 0) {
                            if (data.record_type === 'A' || data.record_type === 'AAAA') {
                                output += `IP Addresses:\\n`;
                                data.records.forEach(record => {
                                    output += `  ${record.value} (TTL: ${record.ttl}s)\\n`;
                                });
                            } else if (data.record_type === 'MX') {
                                output += `Mail Servers:\\n`;
                                data.records.sort((a, b) => a.preference - b.preference).forEach(record => {
                                    output += `  ${record.value} (Preference: ${record.preference}, TTL: ${record.ttl}s)\\n`;
                                });
                            } else if (data.record_type === 'NS') {
                                output += `Name Servers:\\n`;
                                data.records.forEach(record => {
                                    output += `  ${record.value} (TTL: ${record.ttl}s)\\n`;
                                });
                            } else if (data.record_type === 'TXT') {
                                output += `TXT Records:\\n`;
                                data.records.forEach(record => {
                                    output += `  ${record.value} (TTL: ${record.ttl}s)\\n`;
                                });
                            } else if (data.record_type === 'SOA') {
                                output += `SOA Record:\\n`;
                                data.records.forEach(record => {
                                    output += `  Primary NS: ${record.mname}\\n`;
                                    output += `  Email: ${record.rname}\\n`;
                                    output += `  Serial: ${record.serial}\\n`;
                                    output += `  Refresh: ${record.refresh}s\\n`;
                                    output += `  Retry: ${record.retry}s\\n`;
                                    output += `  Expire: ${record.expire}s\\n`;
                                    output += `  Minimum TTL: ${record.minimum}s\\n`;
                                    output += `  TTL: ${record.ttl}s\\n`;
                                });
                            } else if (data.record_type === 'CNAME') {
                                output += `Canonical Names:\\n`;
                                data.records.forEach(record => {
                                    output += `  ${record.value} (TTL: ${record.ttl}s)\\n`;
                                });
                            } else {
                                output += `Records:\\n`;
                                data.records.forEach(record => {
                                    output += `  ${record.value} (TTL: ${record.ttl}s)\\n`;
                                });
                            }
                        } else {
                            output += `No records found.`;
                        }
                    } else {
                        output = `Reverse DNS Lookup Results for ${data.ip_address}:\\n`;
                        output += `Found hostname in ${data.response_time.toFixed(4)} seconds\\n\\n`;
                        output += `Hostname: ${data.hostname}\\n`;
                        
                        if (data.aliases && data.aliases.length > 0) {
                            output += `Aliases:\\n`;
                            data.aliases.forEach(alias => {
                                output += `  ${alias}\\n`;
                            });
                        }
                    }
                    
                    resultDiv.innerHTML = output;
                    resultDiv.classList.remove('error');
                } else {
                    resultDiv.innerHTML = `Error: ${data.error}`;
                    resultDiv.classList.add('error');
                }
                
                resultDiv.style.display = 'block';
                document.getElementById('dnsLoading').style.display = 'none';
            })
            .catch(error => {
                const resultDiv = document.getElementById('dnsResult');
                resultDiv.innerHTML = `Error: ${error.message}`;
                resultDiv.classList.add('error');
                resultDiv.style.display = 'block';
                document.getElementById('dnsLoading').style.display = 'none';
            });
        });
    </script>
</body>
</html>
    ''')

# API 엔드포인트 설정
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ping', methods=['POST'])
def api_ping():
    data = request.get_json()
    
    if not data or 'host' not in data:
        return jsonify({'success': False, 'error': 'Host is required'}), 400
    
    host = data['host']
    count = data.get('count', 5)
    timeout = data.get('timeout', 2)
    
    try:
        result = ping_host(host, count, timeout)
        result['success'] = True
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.get_json()
    
    if not data or 'host' not in data:
        return jsonify({'success': False, 'error': 'Host is required'}), 400
    
    host = data['host']
    scan_type = data.get('scan_type', 'range')
    timeout = data.get('timeout', 0.5)
    advanced = data.get('advanced', False)
    adaptive_timeout = data.get('adaptive_timeout', False)
    
    try:
        if scan_type == 'common':
            # 공통 포트 스캔
            common_ports = get_common_ports()
            
            # 각 포트 개별적으로 스캔
            open_ports = []
            for port in common_ports:
                port_result = scan_host(host, (port, port), timeout, 
                                      use_advanced_options=advanced,
                                      use_adaptive_timeout=adaptive_timeout)
                if port_result['open_ports']:
                    open_ports.extend(port_result['open_ports'])
            
            # 결과 구성
            result = {
                'success': True,
                'host': host,
                'open_ports': open_ports,
                'total_ports_scanned': len(common_ports),
                'scan_time': sum(p.get('response_time', 0) for p in open_ports) if open_ports else 0
            }
            
        else:
            # 포트 범위 스캔
            start_port = data.get('start_port', 1)
            end_port = data.get('end_port', 1024)
            
            if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                return jsonify({'success': False, 'error': 'Port numbers must be between 1 and 65535'}), 400
            
            result = scan_host(host, (start_port, end_port), timeout,
                              use_advanced_options=advanced,
                              use_adaptive_timeout=adaptive_timeout)
            result['success'] = True
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dns', methods=['POST'])
def api_dns():
    data = request.get_json()
    
    if not data or 'lookup_type' not in data:
        return jsonify({'success': False, 'error': 'Lookup type is required'}), 400
    
    lookup_type = data['lookup_type']
    timeout = data.get('timeout', 2.0)
    
    try:
        if lookup_type == 'forward':
            if 'domain' not in data:
                return jsonify({'success': False, 'error': 'Domain is required for forward lookup'}), 400
            
            domain = data['domain']
            record_type = data.get('record_type', 'A')
            
            result = dns_lookup(domain, record_type, timeout)
            if result['success']:
                return jsonify(result)
            else:
                return jsonify({'success': False, 'error': result['error']}), 400
                
        elif lookup_type == 'reverse':
            if 'ip' not in data:
                return jsonify({'success': False, 'error': 'IP address is required for reverse lookup'}), 400
            
            ip = data['ip']
            
            result = reverse_dns_lookup(ip, timeout)
            if result['success']:
                return jsonify(result)
            else:
                return jsonify({'success': False, 'error': result['error']}), 400
                
        else:
            return jsonify({'success': False, 'error': 'Invalid lookup type'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    data = request.get_json()
    
    if not data or 'host' not in data:
        return jsonify({'success': False, 'error': 'Host is required'}), 400
    
    host = data['host']
    
    try:
        # 자동 최적화 실행
        optimal_params = PerformanceOptimizer.auto_optimize_scan_params(host)
        
        # 최적화된 파라미터로 스캔 실행
        scan_result = scan_host(
            host,
            timeout=optimal_params['timeout'],
            max_workers=optimal_params['max_workers'],
            use_advanced_options=optimal_params['use_advanced_options'],
            use_adaptive_timeout=optimal_params['use_adaptive_timeout']
        )
        
        result = {
            'success': True,
            'host': host,
            'optimal_params': optimal_params,
            'scan_result': scan_result
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/benchmark', methods=['POST'])
def api_benchmark():
    data = request.get_json()
    
    if not data or 'host' not in data:
        return jsonify({'success': False, 'error': 'Host is required'}), 400
    
    host = data['host']
    port_count = data.get('port_count', 20)
    
    try:
        # 성능 벤치마크 실행
        benchmark_results = run_performance_benchmark(host, port_count)
        benchmark_results['success'] = True
        
        return jsonify(benchmark_results)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/server-status', methods=['GET'])
def api_server_status():
    try:
        from datetime import datetime
        import time
        
        # 현재 시간
        check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Docker 서비스 상태 확인
        docker_services = [
            {'name': 'TCP Echo Server', 'port': 8080},
            {'name': 'UDP Echo Server', 'port': 8081},
            {'name': 'File Transfer Server', 'port': 8082},
            {'name': 'Web Interface', 'port': 5000}
        ]
        
        for service in docker_services:
            try:
                # 간단한 포트 연결 테스트
                start_time = time.time()
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(1.0)
                result = test_socket.connect_ex(('localhost', service['port']))
                response_time = time.time() - start_time
                test_socket.close()
                
                service['accessible'] = (result == 0)
                service['response_time'] = response_time if service['accessible'] else None
            except Exception:
                service['accessible'] = False
                service['response_time'] = None
        
        result = {
            'success': True,
            'check_time': check_time,
            'docker_services': docker_services
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/monitoring-config', methods=['GET'])
def api_monitoring_config():
    try:
        import yaml
        import os
        
        config_file = 'monitor_config.yaml'
        config_exists = os.path.exists(config_file)
        
        result = {
            'success': True,
            'config_file': config_file,
            'config_exists': config_exists
        }
        
        if config_exists:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                if config:
                    result['monitors'] = config.get('monitors', [])
                    result['alerts'] = config.get('alerts', {})
                else:
                    result['monitors'] = []
                    result['alerts'] = {}
                    
            except Exception as e:
                result['config_exists'] = False
                result['error'] = f'Failed to read config: {str(e)}'
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
