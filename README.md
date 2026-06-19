# 📊 Mini Project Conversational Analytics: Studi Kasus A - HR Analitik

**Dibuat oleh:** Mohammad Aris Darmawan

---

## 📖 Deskripsi Proyek
Proyek ini adalah sebuah aplikasi web *chatbot* berbasis **Text-to-SQL** yang dirancang untuk mempermudah tim Human Capital (HR) dalam menganalisis data pegawai. Aplikasi ini memungkinkan pengguna untuk menanyakan informasi terkait data sumber daya manusia menggunakan bahasa Indonesia sehari-hari. 

Di balik layar, aplikasi memanfaatkan kecerdasan buatan (LLM Google Gemini) untuk menerjemahkan pertanyaan tersebut menjadi *query* PostgreSQL yang valid, mengeksekusinya secara langsung ke database *cloud* (Supabase), dan menyajikan hasilnya dalam bentuk tabel serta visualisasi grafik (otomatis).

## ✨ Fitur Utama
1. 💬 **Natural Language to SQL:** Mengonversi pertanyaan bahasa natural menjadi *query* analitik PostgreSQL dengan akurasi tinggi.
2. 🛡️ **Validasi Keamanan (Guardrails):** Dilengkapi dengan filter keamanan untuk mencegah injeksi SQL dan memblokir perintah berbahaya (seperti `DROP`, `DELETE`, `UPDATE`, `INSERT`).
3. 📈 **Visualisasi Cerdas Otomatis:** Mendeteksi bentuk data hasil *query* dan secara otomatis merender grafik yang sesuai (*Bar chart* untuk data kategorikal, *Line chart* untuk data deret waktu).
4. ☁️ **Cloud-Ready:** Menggunakan Supabase (PostgreSQL) sebagai penyimpanan data dan Streamlit untuk antarmuka pengguna yang siap di-*deploy*.

## 🛠️ Tech Stack
- **Frontend & UI:** [Streamlit](https://streamlit.io/)
- **LLM / AI Engine:** [Google Gemini 1.5 Flash](https://aistudio.google.com/) (`google-genai` SDK)
- **Database:** [Supabase](https://supabase.com/) (PostgreSQL)
- **Data Processing & Viz:** Pandas, Matplotlib, SQLAlchemy

## 🗄️ Skema Database
Aplikasi ini berjalan di atas skema relasional berikut:
- `employees(nip, nama, divisi, jabatan, join_date)`
- `trainings(training_id, nama_diklat, tanggal)`
- `enrollments(nip, training_id, status, nilai)`

*(Relasi: `enrollments.nip` -> `employees.nip`, `enrollments.training_id` -> `trainings.training_id`)*

## 🚀 Cara Menjalankan Aplikasi Secara Lokal

### 1. Prasyarat
Pastikan Anda telah menginstal Python 3.9 atau yang lebih baru.

### 2. Instalasi Dependensi
Clone repositori ini, lalu instal semua *library* yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Secrets (API Key & Database)
Buat sebuah folder bernama `.streamlit` di dalam direktori proyek utama Anda. Di dalam folder tersebut, buat file `secrets.toml` dan isi dengan kredensial Anda:

```toml
# File: .streamlit/secrets.toml
GEMINI_API_KEY = "masukkan_api_key_gemini_anda_di_sini"
DB_URL = "postgresql://postgres.[project-ref]:[password]@aws-0-[region][.pooler.supabase.com:6543/postgres](https://.pooler.supabase.com:6543/postgres)"
```
*(Catatan: Jangan pernah melakukan commit file `secrets.toml` ke GitHub publik).*

### 4. Jalankan Aplikasi
Eksekusi perintah berikut di terminal Anda:
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser pada alamat `http://localhost:8501`.

## 💡 Contoh Pertanyaan (Use Cases)
Anda dapat mencoba menanyakan hal-hal berikut di dalam *chatbox*:
- *"Berapa jumlah pegawai per divisi?"*
- *"Siapa yang belum mengikuti diklat Data Engineering?"*
- *"Berapa rata-rata nilai diklat per unit (divisi)?"*
- *"Tampilkan 5 pegawai yang paling baru bergabung!"*

---
*Proyek ini dikembangkan sebagai bagian dari Mini Project Conversational Analytics.*
