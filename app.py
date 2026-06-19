import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from google import genai
import re

# ==========================================
# 1. KONFIGURASI HALAMAN & DATABASE
# ==========================================
st.set_page_config(page_title="AI Human Capital Analytics", page_icon="📊", layout="wide")
st.title("📊 Chatbot Data Human Capital")
st.caption("Tanyakan insight data pegawai menggunakan bahasa sehari-hari. Didukung oleh Gemini AI & PostgreSQL.")

# Ambil secrets (Pastikan .streamlit/secrets.toml sudah diisi)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
DB_URL = st.secrets["DB_URL"]

# Setup Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Setup Database Connection (di-cache agar tidak bolak-balik konek)
@st.cache_resource
def init_connection():
    return create_engine(DB_URL)

engine = init_connection()

# ==========================================
# 2. FUNGSI INTI (PIPELINE TEXT-TO-SQL)
# ==========================================
SCHEMA_STR = """
employees(nip, nama, divisi, jabatan, join_date)
trainings(training_id, nama_diklat, tanggal)
enrollments(nip, training_id, status, nilai)

Relasi:
- enrollments.nip -> employees.nip
- enrollments.training_id -> trainings.training_id
"""

def build_prompt(question: str) -> str:
    return f"""Anda adalah ahli data engineer PostgreSQL. 
Tugas Anda adalah mengubah bahasa natural menjadi SATU query SQL PostgreSQL yang valid.

ATURAN KETAT:
1. Berikan HANYA sintaks SQL murni. 
2. JANGAN berikan penjelasan, salam, atau teks awalan/akhiran apa pun.
3. JANGAN gunakan format markdown.
4. Hanya gunakan tabel dan kolom yang ada pada skema di bawah ini.
5. Jika ada nilai yang tidak pasti, gunakan ILIKE.

SKEMA DATABASE:
{SCHEMA_STR}

Pertanyaan: {question}
SQL:"""

def generate_sql(question: str) -> str:
    prompt = build_prompt(question)
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt
    )
    # Bersihkan markdown jika terbawa
    sql_clean = response.text.replace("```sql", "").replace("```", "").strip()
    return sql_clean

def validate_sql(sql: str) -> bool:
    FORBIDDEN = ["drop", "delete", "update", "insert", "alter", "truncate", "create", "grant"]
    if not sql or not sql.strip(): return False
    sql_lower = sql.strip().lower()
    if not sql_lower.startswith("select"): return False
    for word in FORBIDDEN:
        if re.search(rf'\b{word}\b', sql_lower): return False
    if ";" in sql.strip().rstrip(";"): return False
    return True

def visualize_in_streamlit(df: pd.DataFrame):
    if df.empty or df.shape[1] != 2:
        return 
        
    col1, col2 = df.columns[0], df.columns[1]
    is_num1 = pd.api.types.is_numeric_dtype(df[col1])
    is_num2 = pd.api.types.is_numeric_dtype(df[col2])
    
    if is_num1 == is_num2: return
        
    x_col, y_col = (col1, col2) if not is_num1 else (col2, col1)

    fig, ax = plt.subplots(figsize=(8, 4))
    
    if pd.api.types.is_datetime64_any_dtype(df[x_col]):
        df_sorted = df.sort_values(by=x_col)
        ax.plot(df_sorted[x_col], df_sorted[y_col], marker='o', color='#1f77b4')
    else:
        ax.bar(df[x_col].astype(str), df[y_col], color='#1f77b4')
        plt.xticks(rotation=45, ha='right')

    ax.set_xlabel(x_col.title())
    ax.set_ylabel(y_col.title())
    ax.set_title(f"{y_col.title()} berdasarkan {x_col.title()}")
    plt.tight_layout()
    
    st.pyplot(fig) # Render plot ke Streamlit

# ==========================================
# 3. ANTARMUKA CHAT STREAMLIT
# ==========================================
# Simpan riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            with st.expander("Lihat Query SQL"):
                st.code(msg["sql"], language="sql")
        if "df" in msg:
            st.dataframe(msg["df"], use_container_width=True)
            visualize_in_streamlit(msg["df"])

# Input user
if prompt := st.chat_input("Contoh: Berapa jumlah pegawai per divisi?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Meracik SQL dan mengambil data..."):
            try:
                # 1. Generate & Validasi
                sql = generate_sql(prompt)
                
                if not validate_sql(sql):
                    # Retry 1x jika gagal validasi
                    sql = generate_sql(prompt)
                    if not validate_sql(sql):
                        st.error("Maaf, pertanyaan menghasilkan query yang tidak diizinkan.")
                        st.stop()
                
                # 2. Tampilkan SQL (dalam expander agar tidak menuhi chat)
                with st.expander("Lihat Query SQL", expanded=True):
                    st.code(sql, language="sql")
                
                # 3. Eksekusi Query
                with engine.connect() as conn:
                    df = pd.read_sql(text(sql), conn)
                
                # 4. Tampilkan Tabel & Grafik
                st.dataframe(df, use_container_width=True)
                visualize_in_streamlit(df)
                
                # 5. Simpan ke riwayat
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Berikut adalah data yang Anda minta:", 
                    "sql": sql, 
                    "df": df
                })
                
            except Exception as e:
                st.error(f"Terjadi kesalahan pada database:\n{e}")
