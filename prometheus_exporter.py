from flask import Flask, request, jsonify, Response
import requests
import time
import psutil  # Untuk monitoring sistem (CPU/RAM)
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- DEFINISI METRIK PROMETHEUS ---
# 1. Menghitung Total Request (Counter: hanya bisa naik)
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests')

# 2. Menghitung Kecepatan Respon (Histogram: distribusi waktu)
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency')

# 3. Menghitung Throughput (Counter)
THROUGHPUT = Counter('http_requests_throughput', 'Total number of requests per second')

# 4. Metrik Kesehatan Sistem (Gauge: bisa naik turun)
CPU_USAGE = Gauge('system_cpu_usage', 'CPU Usage Percentage')
RAM_USAGE = Gauge('system_ram_usage', 'RAM Usage Percentage')

# --- ENDPOINT 1: UNTUK PROMETHEUS (/metrics) ---
@app.route('/metrics', methods=['GET'])
def metrics():
    # Update status CPU & RAM setiap kali Prometheus "mengetuk pintu"
    CPU_USAGE.set(psutil.cpu_percent(interval=None)) 
    RAM_USAGE.set(psutil.virtual_memory().percent)
    
    # Berikan semua data dalam format khusus Prometheus
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# --- ENDPOINT 2: UNTUK USER (/predict) ---
# User menembak ke sini (Port 8000), lalu kita teruskan ke Docker (Port 5005)
@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    REQUEST_COUNT.inc() # Catat ada tamu datang
    THROUGHPUT.inc()

    # Oper ke Model Asli (Docker Container)
    api_url = "http://127.0.0.1:5005/invocations"
    data = request.get_json()

    try:
        # Kirim ke Docker
        response = requests.post(api_url, json=data)
        
        # Hitung durasi
        duration = time.time() - start_time
        REQUEST_LATENCY.observe(duration) # Catat durasi
        
        # Balikin jawaban ke User
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Jalan di Port 8000 (Beda dengan Docker 5005)
    print("🚀 Exporter berjalan di http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000)