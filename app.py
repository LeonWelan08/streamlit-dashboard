import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="Semantic Similarity Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BACA EXCEL
df_w2v = pd.read_excel(
 "hasil_word2vec.xlsx"
)

df_bert = pd.read_excel(
 "hasil_indobert.xlsx"
)

# ================= CSS KUSTOM =================
st.markdown("""
<style>
/* 1. Sidebar Background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E1E2F, #2D2D44);
}

/* 2. Warna teks Sidebar (Hanya targetkan teks, bukan semua elemen) */
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* 3. Hover menu radio navigasi */
div[role="radiogroup"] label:hover {
    background-color: #FF69B4;
    border-radius: 10px;
    transition: 0.3s;
}

/* ============================================== */
/* 4. KUSTOMISASI KOTAK UPLOAD */
/* ============================================== */

/* Wadah luar kotak upload (warna dasar, border, & ukuran) */
[data-testid="stFileUploader"] section {
    background-color: rgba(31, 119, 180, 0.10) !important; /* Pink Transparan */
    border: 1.5px dashed #1f77b4 !important; /* Garis tepi pink */
    border-radius: 10px !important;
    padding: 10px !important; /* Mengecilkan padding agar kotak jadi ramping */
}

/* Menghilangkan background putih yang memaksa dari bawaan Streamlit */
[data-testid="stFileUploader"] section * {
    background-color: transparent !important;
}

/* Tombol Upload di dalamnya dibuat lebih tegas */
[data-testid="stFileUploader"] button {
    background-color: #1f77b4 !important; /* Warna kancing Pink */
    color: white !important; /* Teks putih */
    border: none !important;
    border-radius: 5px !important;
    min-height: 35px !important;
    font-weight: bold !important;
}

/* Efek tombol upload jika disentuh */
[data-testid="stFileUploader"] button:hover {
    background-color: #1E1E2F !important;
    color: white !important;
}

/* ============================================== */
/* 5. CSS Dashboard Utama (Card Metric & Tabs)    */
/* ============================================== */
h1 { font-size: 38px !important; font-weight: 700 !important; }
h2 { font-size: 28px !important; font-weight: 600 !important; }
h3 { font-size: 22px !important; }
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
}
[data-testid="stMetricValue"] {
    font-size: 32px !important;
    color: #1f77b4 !important;
}
.stTabs [data-baseweb="tab-list"] { gap: 20px; }
.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: #f0f2f6;
    border-radius: 5px 5px 0px 0px;
    padding: 10px 20px;
}
</style>
""", unsafe_allow_html=True)

# ================= FUNGSI PENCARIAN =================
def search_top(df, query, sim_col="Similarity", doc_col="Top_Document"):
    data = df[df["Query"].str.contains(query, case=False, na=False)]
    
    if data.empty:
        return None, 0
        
    top = data.sort_values(sim_col, ascending=False).iloc[0]
    
    return top[doc_col], top[sim_col]


# ================= SIDEBAR & UPLOAD =================
st.sidebar.markdown("<h2 style='text-align:center;'> Dashboard Kemiripan Semantik</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("###  Upload Data")
file_bert = st.sidebar.file_uploader("Upload Data 1 (.xlsx)", type=["xlsx"])
file_w2v = st.sidebar.file_uploader("Upload Data 2 (.xlsx)", type=["xlsx"])

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigasi Utama",
    ["Dashboard", "Pencarian", "Hasil Analisis", "IndoBERT VS Word2Vec"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Sistem Analisis Kemiripan Semantik**\n
    Membandingkan algoritma klasifikasi teks
    """
)

# ================= LOGIKA DINAMIS =================
# Cek apakah file sudah diunggah
if file_bert is not None and file_w2v is not None:
    try:
        # Membaca data yang diunggah
        df_bert = pd.read_excel(file_bert)
        df_w2v = pd.read_excel(file_w2v)
        data_ready = True
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        data_ready = False
else:
    data_ready = False

# ================= KONTEN HALAMAN =================

if menu == "Dashboard":
    st.title(" Beranda Dashboard Kemiripan Semantik")
    if not data_ready:
        st.warning(" Selamat datang! Silakan unggah file Excel pada menu di sidebar sebelah kiri untuk menampilkan data.")
    else:
        st.success("✅ Data berhasil dimuat! Silakan gunakan menu navigasi untuk melihat analisis.")
        st.markdown("""
            Sistem perbandingan **KEMIRIPAN SEMANTIK** Anda sekarang sudah terhubung dengan data dinamis yang baru saja Anda unggah.
            - Buka menu **Pencarian** untuk mencoba semantic search.
            - Buka menu **Hasil Analisis** untuk melihat grafik dan metrik.
        """)

elif menu == "Pencarian":
    st.title("Semantic Similarity Checker")
    
    if not data_ready: # Peringatan jika belum upload excel
        st.warning("Harap unggah data di sidebar terlebih dahulu.")
    else:
        st.markdown("Masukkan kueri teks di bawah ini untuk melihat dokumen teratas yang paling mirip menurut model IndoBERT dan Word2Vec.")
        
        query = st.text_input("Masukkan Kueri Pencarian", placeholder="Ketik kata kunci...")

        if st.button("Periksa Kemiripan", use_container_width=True):
            if query:
                with st.spinner("Sedang mencari..."):
                    import time
                    time.sleep(0.5) # Efek loading sebentar
                    
                    # Memanggil fungsi asli
                    bert_doc, bert_score = search_top(df_bert, query)
                    w2v_doc, w2v_score = search_top(df_w2v, query)

                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(" **Hasil Data 1**")
                    if bert_doc:
                        st.markdown(f"**Skor Similarity:** `{bert_score}`")
                        st.info(bert_doc)
                    else:
                        st.warning("Tidak ditemukan kecocokan kueri.")

                with col2:
                    st.info(" **Hasil Data 2**")
                    if w2v_doc:
                        st.markdown(f"**Skor Similarity:** `{w2v_score}`")
                        st.success(w2v_doc)
                    else:
                        st.warning("Tidak ditemukan kecocokan kueri.")
            else:
                st.warning("Harap masukkan kueri terlebih dahulu!")

elif menu == "Hasil Analisis":
    st.title(" Hasil Analisis Komparasi")
    
    if not data_ready:
        st.warning("Harap unggah data di sidebar terlebih dahulu.")
    else:
        tab1, tab2, tab3 = st.tabs([" Metrik & Tren", " Analisis Indikator", " Detail Tabel Data"])

        # TAB 1: METRIK & TREN (Dihitung Otomatis)
        with tab1:
            st.subheader("Skor Kemiripan Rata-Rata")
            col1, col2 = st.columns(2)
            
            # Perhitungan dinamis rata-rata
            bert_mean = df_bert["Similarity"].mean() if "Similarity" in df_bert.columns else 0
            w2v_mean = df_w2v["Similarity"].mean() if "Similarity" in df_w2v.columns else 0
            
            col1.metric("Rata-rata Data 1", round(bert_mean, 4), delta="Model A")
            col2.metric("Rata-rata Data 2", round(w2v_mean, 4), delta="Model B", delta_color="off")

            st.divider()
            st.subheader("Tren Perbandingan Similarity")
            
            if "Query_Index" in df_bert.columns and "Similarity" in df_bert.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_bert["Query_Index"], y=df_bert["Similarity"], mode="lines+markers", name="Data 1", line=dict(color="#FF69B4"), marker=dict(color="#FF69B4")))
                fig.add_trace(go.Scatter(x=df_w2v["Query_Index"], y=df_w2v["Similarity"], mode="lines+markers", name="Data 2", line=dict(color="#36A2EB"), marker=dict(color="#36A2EB")))
                fig.update_layout(xaxis_title="Query Index", yaxis_title="Similarity Score", hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Grafik tidak dapat ditampilkan karena kolom 'Query_Index' atau 'Similarity' tidak ditemukan dalam data unggahan.")

        # TAB 2: ANALISIS INDIKATOR (Dihitung Otomatis dari kolom 'Indikator')
        with tab2:
            st.subheader("Distribusi Indikator yang Muncul")
            
            # Cek apakah kolom Top_Doc_Index dan Indikator ada di dataset
            if "Top_Doc_Index" in df_bert.columns and "Top_Doc_Index" in df_w2v.columns and "Top_Document" in df_bert.columns:
                
                # ================= GRAFIK INDOBERT =================
                # Menghitung berdasarkan Top_Doc_Index
                df_indo_count = df_bert["Top_Doc_Index"].value_counts().reset_index()
                df_indo_count.columns = ["Top_Doc_Index", "Jumlah"]
                
                # Membuat label agar rapi (Contoh: "Indikator 12")
                df_indo_count["Label_Indikator"] = "Indikator " + df_indo_count["Top_Doc_Index"].astype(str)

                fig_indo = px.bar(
                    df_indo_count, 
                    x="Label_Indikator", 
                    y="Jumlah", 
                    text="Jumlah", 
                    title="Frekuensi Indikator - Data 1", 
                    color_discrete_sequence=["#FF69B4"]
                )
                fig_indo.update_layout(height=450, xaxis_tickangle=-45)
                st.plotly_chart(fig_indo, use_container_width=True)

                # ================= GRAFIK WORD2VEC =================
                df_w2v_count = df_w2v["Top_Doc_Index"].value_counts().reset_index()
                df_w2v_count.columns = ["Top_Doc_Index", "Jumlah"]
                df_w2v_count["Label_Indikator"] = "Indikator " + df_w2v_count["Top_Doc_Index"].astype(str)

                fig_w2v = px.bar(
                    df_w2v_count, 
                    x="Label_Indikator", 
                    y="Jumlah", 
                    text="Jumlah", 
                    title="Frekuensi Indikator - Data 2", 
                    color_discrete_sequence=["#36A2EB"]
                )
                fig_w2v.update_layout(height=450, xaxis_tickangle=-45)
                st.plotly_chart(fig_w2v, use_container_width=True)

                st.divider()

                # ================= TABEL 5 INDIKATOR TERBANYAK =================
                # Kita buat mapping (kamus) agar angka index bisa dikembalikan ke teks panjangnya untuk ditampilkan di tabel
                mapping_indo = df_bert[['Top_Doc_Index', 'Top_Document']].drop_duplicates()
                mapping_w2v = df_w2v[['Top_Doc_Index', 'Top_Document']].drop_duplicates()

                st.markdown("#####  5 Indikator Terbanyak Data 1")
                df_top_indo = df_indo_count.head(5).copy()
                
                # Gabungkan data jumlah dengan teks asli indikatornya
                df_top_indo = pd.merge(df_top_indo, mapping_indo, on="Top_Doc_Index", how="left")
                df_top_indo.insert(0, 'No', range(1, len(df_top_indo) + 1))
                
                # Menampilkan tabel dengan urutan: No, Label_Indikator, Teks Asli, Jumlah
                st.dataframe(df_top_indo[['No', 'Label_Indikator', 'Top_Document', 'Jumlah']], hide_index=True, use_container_width=True)
                
                st.write("") # Spasi pemisah

                st.markdown("#####  5 Indikator Terbanyak Data 2")
                df_top_w2v = df_w2v_count.head(5).copy()
                df_top_w2v = pd.merge(df_top_w2v, mapping_w2v, on="Top_Doc_Index", how="left")
                df_top_w2v.insert(0, 'No', range(1, len(df_top_w2v) + 1))
                
                st.dataframe(df_top_w2v[['No', 'Label_Indikator', 'Top_Document', 'Jumlah']], hide_index=True, use_container_width=True)

            else:
                st.warning(" Kolom bernama 'Top_Doc_Index' atau 'Indikator' tidak ditemukan di file Excel Anda.")

        # TAB 3: DETAIL TABEL DATA
        with tab3:
            st.subheader("Raw Data (Data Mentah)")
            with st.expander(" Buka Tabel Data 1", expanded=True):
                st.dataframe(df_bert, use_container_width=True, height=400)
            with st.expander(" Buka Tabel Data 2"):
                st.dataframe(df_w2v, use_container_width=True, height=400)

elif menu == "IndoBERT VS Word2Vec":
    st.title("Hasil Perbandingan IndoBERT VS Word2Vec")
    st.markdown("Perbandingan mendalam antara performa **IndoBERT** dan **Word2Vec**.")

    # Membuat Tabs agar lebih rapi
    tab1, tab2, tab3 = st.tabs(["Metrik & Tren", "Analisis Indikator", "Detail Tabel Data"])

    # TAB 1: Metrik Utama & Grafik Garis
    with tab1:
        st.subheader("Skor Kemiripan Rata-Rata")
        col1, col2 = st.columns(2)
        
        # Validasi jika dataframe kosong saat tidak ada file excel
        bert_mean = df_bert["Similarity"].mean() if not df_bert.empty else 0
        w2v_mean = df_w2v["Similarity"].mean() if not df_w2v.empty else 0
        
        col1.metric("Rata-rata IndoBERT", round(bert_mean, 4), delta="Model A")
        col2.metric("Rata-rata Word2Vec", round(w2v_mean, 4), delta="Model B", delta_color="off")

        st.divider()
        st.subheader("Tren Perbandingan Similarity")
        
        fig = go.Figure()
        if not df_bert.empty and not df_w2v.empty:
            fig.add_trace(go.Scatter(x=df_bert["Query_Index"], y=df_bert["Similarity"], mode="lines+markers", name="IndoBERT", line=dict(color="#FF69B4"), marker=dict(color="#FF69B4")))
            fig.add_trace(go.Scatter(x=df_w2v["Query_Index"], y=df_w2v["Similarity"], mode="lines+markers", name="Word2Vec", line=dict(color="#36A2EB"), marker=dict(color="#36A2EB")))
        
        fig.update_layout(xaxis_title="Query Index", yaxis_title="Similarity Score", hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Evaluasi Performa Model")
        eval_col1, eval_col2 = st.columns(2)
        
        with eval_col1:
            st.markdown("#### IndoBERT")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", "70.4%")
            c2.metric("Recall", "83.3%")
            c3.metric("Precision", "50.4%")
            c4.metric("F1 Score", "62.6%")
            
        with eval_col2:
            st.markdown("#### Word2Vec")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", "72.5%")
            c2.metric("Recall", "80.4%")
            c3.metric("Precision", "58.8%")
            c4.metric("F1 Score", "67.8%")

    # TAB 2: Distribusi Indikator & Top 5
    with tab2:
        st.subheader("Distribusi Indikator yang Muncul")
        
        # Data IndoBERT
        indo_labels = ['Indikator 1','Indikator 4','Indikator 8','Indikator 11','Indikator 12', 'Indikator 19','Indikator 20','Indikator 21','Indikator 22','Indikator 28', 'Indikator 29','Indikator 30','Indikator 31','Indikator 33','Indikator 34', 'Indikator 35','Indikator 36','Indikator 37','Indikator 40','Indikator 41', 'Indikator 43','Indikator 47','Indikator 48','Indikator 49','Indikator 50', 'Indikator 54','Indikator 44','Indikator 57','Indikator 58','Indikator 60', 'Indikator 61']
        indo_data = [10,1,9,28,77,5,8,1,14,2,5,4,4,61,48,1,1,4, 25,21,106,2,57,2,52,2,6,2,2,30,2]
        df_indo = pd.DataFrame({"Indikator": indo_labels, "Jumlah": indo_data})
        
        fig_indo = px.bar(df_indo, x="Indikator", y="Jumlah", text="Jumlah", title="Frekuensi Indikator - IndoBERT", color_discrete_sequence=["#FF69B4"])
        fig_indo.update_layout(height=450, xaxis_tickangle=-45)
        st.plotly_chart(fig_indo, use_container_width=True)

        # Data Word2Vec
        w2v_labels = ['Indikator 1','Indikator 2','Indikator 3','Indikator 6','Indikator 9', 'Indikator 10','Indikator 11','Indikator 12','Indikator 13','Indikator 14', 'Indikator 15','Indikator 16','Indikator 17','Indikator 19','Indikator 20', 'Indikator 21','Indikator 22','Indikator 24','Indikator 25','Indikator 28', 'Indikator 29','Indikator 30','Indikator 32','Indikator 33','Indikator 35', 'Indikator 37','Indikator 38','Indikator 39','Indikator 40','Indikator 41', 'Indikator 43','Indikator 44','Indikator 45','Indikator 46','Indikator 47', 'Indikator 48','Indikator 49','Indikator 50','Indikator 52','Indikator 53', 'Indikator 54','Indikator 55','Indikator 56','Indikator 57','Indikator 58', 'Indikator 60','Indikator 61']
        w2v_data = [10,28,2,2,5,6,70,79,1,8,2,6,25,10,4,12,15,14,7, 24,29,9,1,3,4,13,6,6,25,2,1,1,3,1,6,44,18,4,4,5,44, 9,10,1,4,4,5]
        df_w2v_chart = pd.DataFrame({"Indikator": w2v_labels, "Jumlah": w2v_data})
        
        fig_w2v = px.bar(df_w2v_chart, x="Indikator", y="Jumlah", text="Jumlah", title="Frekuensi Indikator - Word2Vec", color_discrete_sequence=["#36A2EB"])
        fig_w2v.update_layout(height=450, xaxis_tickangle=-45)
        st.plotly_chart(fig_w2v, use_container_width=True)

        st.divider()
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("##### 5 Indikator Terbanyak IndoBERT")
            df_top_indo = pd.DataFrame({"No":[1,2,3,4,5], "Indikator":["Adanya dokumen palsu pencalonan", "Rekomendasi Bawaslu ketidaknetralan", "Perubahan suara rekapitulasi", "Penghitungan suara ulang", "Materi kampanye Hoax"], "Jumlah":[124,120,64,40,30]})
            st.dataframe(df_top_indo, hide_index=True, use_container_width=True)
            
        with col_t2:
            st.markdown("##### 5 Indikator Terbanyak Word2Vec")
            df_top_w2v = pd.DataFrame({"No":[1,2,3,4,5], "Indikator":["TPS tanpa Pengawas", "Surat suara tertukar", "Politik Uang", "Putusan Bawaslu tidak ditindaklanjuti", "Informasi pelanggaran pemungutan suara"], "Jumlah":[139,91,50,47,35]})
            st.dataframe(df_top_w2v, hide_index=True, use_container_width=True)

    # TAB 3: Tabel Data Komprehensif
    with tab3:
        st.subheader("Data Silang (Cross-Comparison)")
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("**Perbandingan Top 5 IndoBERT vs Word2Vec**")
            df_compare_indo = pd.DataFrame({"Indikator":["Dokumen palsu", "Ketidaknetralan", "Perubahan suara", "Hitung ulang", "Kampanye Hoax"], "IndoBERT":[124,120,64,40,30], "Word2Vec":[4,7,7,1,0]})
            st.dataframe(df_compare_indo, hide_index=True, use_container_width=True)
            
        with col_c2:
            st.markdown("**Perbandingan Top 5 Word2Vec vs IndoBERT**")
            df_compare_w2v = pd.DataFrame({"Indikator":["TPS tanpa Pengawas", "Suara tertukar", "Politik uang", "Putusan tak diproses", "Pelanggaran pemungutan"], "Word2Vec":[139,91,50,47,35], "IndoBERT":[0,4,3,0,1]})
            st.dataframe(df_compare_w2v, hide_index=True, use_container_width=True)

        st.markdown("**Confusion Matrix Model**")
        cm_df = pd.DataFrame({"Metric": ["True Positive (TP)", "True Negative (TN)", "False Positive (FP)", "False Negative (FN)"], "IndoBERT": [60, 109, 59, 12], "Word2Vec": [70, 104, 49, 17]})
        st.dataframe(cm_df, hide_index=True, use_container_width=True)
        
        st.divider()
        st.subheader("Raw Data")
        with st.expander("Buka Tabel Dataset Lengkap IndoBERT & Word2Vec"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("**Dataset IndoBERT**")
                st.dataframe(df_bert, use_container_width=True, height=300)
            with col_d2:
                st.markdown("**Dataset Word2Vec**")
                st.dataframe(df_w2v, use_container_width=True, height=300)
