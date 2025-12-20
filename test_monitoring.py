import requests
import json
import time
import logging

# 1. Konfigurasi "Buku Catatan" (Logging)
# File akan disimpan dengan nama 'api_model_logs.log'
logging.basicConfig(
    filename="api_model_logs.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 2. Alamat Model (Toko)
API_URL = "http://127.0.0.1:8000/predict"

# 3. Data Nasabah (Input)
# Kita pakai data dummy yang sesuai dengan format training (PCA)
input_data = {
    "dataframe_split": {
        "columns": [
            "Age", "Credit_Mix", "Payment_of_Min_Amount", "Payment_Behaviour", 
            "pc1_1", "pc1_2", "pc1_3", "pc1_4", "pc1_5", "pc2_1", "pc2_2"
        ],
        "data": [
            # Data Nasabah Contoh
            [25.0, 1, 1, 1, 0.5, -0.2, 1.1, 0.0, -0.5, 0.1, 0.9]
        ]
    }
}

# Siapkan paket data
headers = {"Content-Type": "application/json"}
payload = json.dumps(input_data)

print("🚀 Mengirim data ke model...")

# 4. Mulai Hitung Waktu (Stopwatch Start)
start_time = time.time()

try:
    # Kirim Request ke Docker
    response = requests.post(API_URL, headers=headers, data=payload)
    
    # 5. Stop Waktu (Stopwatch Stop)
    response_time = time.time() - start_time

    # Cek Apakah Sukses (Kode 200 = OK)
    if response.status_code == 200:
        prediction = response.json()
        
        # --- INI INTI MATERI KITA (MENCATAT KE LOG) ---
        logging.info(f"Input: {input_data}, Output: {prediction}, Latency: {response_time:.4f} sec")
        # ----------------------------------------------

        print(f"✅ Sukses! Prediksi: {prediction}")
        print(f"⏱️ Waktu Proses: {response_time:.4f} detik")
        print("📝 Data telah dicatat di 'api_model_logs.log'")
    
    else:
        # Catat Error jika gagal
        logging.error(f"Gagal. Status: {response.status_code}, Pesan: {response.text}")
        print(f"❌ Error {response.status_code}")

except Exception as e:
    # Catat jika server mati/tidak bisa dikontak
    logging.error(f"Koneksi Gagal: {str(e)}")
    print(f"⚠️ Koneksi Gagal: {str(e)}")