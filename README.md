# =====================================================
# PANDUAN MENJALANKAN DASHBOARD
# Restaurant Orders - Visualisasi Data
# =====================================================

## 📋 Langkah-langkah Instalasi

### 1. Install Library
Buka terminal/command prompt, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 2. Setup Database
- Pastikan MySQL/XAMPP sudah berjalan
- Import file `Database.sql` ke MySQL:
  ```bash
  mysql -u root -p < Database.sql
  ```
  Atau gunakan phpMyAdmin untuk import

### 3. Konfigurasi Database
Edit file `config.py` sesuai pengaturan MySQL kamu:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Isi password jika ada
    'database': 'restaurant_orders',
    'port': 3306
}
```

### 4. Jalankan Dashboard
```bash
streamlit run main.py
```

Dashboard akan terbuka di browser: http://localhost:8501

---

## 🎯 Fitur Dashboard

### 1. Filter Interaktif (Sidebar)
- Filter berdasarkan tanggal
- Filter berdasarkan kategori menu
- Filter berdasarkan tipe layanan
- Filter berdasarkan metode pembayaran
- Filter berdasarkan status order

### 2. Tab Dashboard Utama
- Tren penjualan harian
- Penjualan per kategori (Pie Chart)
- Top 10 menu terlaris
- Metode pembayaran
- Tipe layanan (Dine In vs Take Away)
- Pesanan per jam

### 3. Tab Analisis Menu
- Top N menu terlaris (slider)
- Tabel detail penjualan menu

### 4. Tab Pelanggan & Review
- Distribusi rating
- Member vs Guest orders
- Review terbaru

### 5. Tab Reservasi & Meja
- Utilisasi meja
- Status reservasi
- Status meja saat ini

### 6. Tab Study Case
**FITUR KHUSUS untuk menjawab pertanyaan dosen!**

Pilih study case yang tersedia:
1. Total Penjualan per Kategori
2. Menu Paling Laris (Top 10)
3. Analisis Pelanggan
4. Tren Penjualan Bulanan
5. Performa Meja
6. Analisis Metode Pembayaran
7. Analisis Jam Sibuk
8. Analisis Rating & Review
9. Reservasi per Lokasi Meja
10. Perbandingan Dine In vs Take Away

**Custom Query**: Tulis query SQL sendiri!

---

## ❓ Troubleshooting

### Error: ModuleNotFoundError
```bash
pip install streamlit pandas plotly mysql-connector-python
```

### Error: Access denied for user 'root'
Edit password di `config.py`

### Error: Unknown database
Import `Database.sql` terlebih dahulu

---

## 📊 Contoh Query untuk Dosen

Jika dosen meminta visualisasi tertentu, gunakan Tab "Study Case" atau tulis query di "Custom Query":

```sql
-- Contoh 1: Total penjualan per bulan
SELECT MONTHNAME(order_time) as Bulan, SUM(total_price) as Total
FROM Orders o JOIN Order_Details od ON o.order_id = od.order_id
GROUP BY MONTH(order_time)

-- Contoh 2: Menu dengan rating tertinggi
SELECT m.item_name, AVG(r.rating) as AvgRating
FROM Reviews r
JOIN Orders o ON r.order_id = o.order_id
JOIN Order_Details od ON o.order_id = od.order_id
JOIN Menu m ON od.menu_id = m.menu_id
GROUP BY m.item_name
ORDER BY AvgRating DESC
```

---

© 2025 - Restaurant Orders Dashboard
