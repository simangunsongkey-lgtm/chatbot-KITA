import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Setup halaman Streamlit
st.set_page_config(page_title="Super AI Hub", page_icon="🤖", layout="wide")
st.title("🤖 Super AI Hub: Chat, Analisis Media & Generator")

# Sidebar untuk Konfigurasi
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("AIzaSyAiJmfdLDFKANSQ-HhJpXmN_nLEtn-5rqY:", type="password")
    
    # Pilihan Model Konten (Teks/File)
    model_opsi = st.selectbox(
        "Pilih Model AI:",
        ["gemini-1.5-flash", "gemini-1.5-pro"]
    )
    st.caption("💡 *gemini-1.5-flash* lebih cepat, *gemini-1.5-pro* lebih cerdas untuk file besar.")

if not api_key:
    st.warning("⚠️ Silakan masukkan API Key Anda di sidebar untuk memulai.")
    st.stop()

# Konfigurasi Google AI SDK
genai.configure(api_key=api_key)

# Membuat Tabs Fitur
tab1, tab2, tab3 = st.tabs(["💬 Chat & Analisis Multimodal", "🎨 Generator Gambar (Imagen)", "📂 Generator File"])

# ==========================================
# TAB 1: CHAT & ANALISIS MULTIMODAL (Foto, Suara, Video, Dokumen)
# ==========================================
with tab1:
    st.subheader("Minta AI Menganalisis Foto, Suara, Video, atau Dokumen Anda")
    
    # Upload berbagai jenis file
    uploaded_file = st.file_uploader(
        "Unggah File Anda (Gambar, Audio, Video, PDF, TXT):", 
        type=["png", "jpg", "jpeg", "mp3", "wav", "mp4", "mpeg", "pdf", "txt"]
    )
    
    preview_konten = None
    file_payload = None

    if uploaded_file is not None:
        mime_type = uploaded_file.type
        bytes_data = uploaded_file.read()
        file_payload = {"mime_type": mime_type, "data": bytes_data}
        
        # Tampilkan preview berdasarkan tipe file
        if "image" in mime_type:
            preview_konten = Image.open(io.BytesIO(bytes_data))
            st.image(preview_konten, caption="Preview Gambar Anda", width=300)
        elif "audio" in mime_type:
            st.audio(bytes_data, format=mime_type)
        elif "video" in mime_type:
            st.video(bytes_data, format=mime_type)
        elif "pdf" in mime_type or "text" in mime_type:
            st.success(f"📄 File berhasil dimuat: {uploaded_file.name}")

    # Logika Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dari User
    if user_prompt := st.chat_input("Tanyakan sesuatu tentang file Anda atau ketik pesan biasa..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        # Proses oleh AI
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                model = genai.GenerativeModel(model_opsi)
                
                # Jika ada file yang diupload, kirim bersama prompt teks
                if file_payload:
                    konten_kirim = [user_prompt, file_payload]
                    response = model.generate_content(konten_kirim)
                else:
                    response = model.generate_content(user_prompt)
                
                ai_response = response.text
                message_placeholder.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# ==========================================
# TAB 2: GENERATOR GAMBAR (TEXT TO IMAGE)
# ==========================================
with tab2:
    st.subheader("🎨 Buat Foto/Gambar Menggunakan AI (Imagen 3)")
    prompt_gambar = st.text_area("Deskripsikan gambar yang ingin Anda buat secara detail:", placeholder="Contoh: A futuristic city with flying cars at sunset, photorealistic, 4k resolution")
    
    if st.button("Generate Gambar"):
        if prompt_gambar:
            with st.spinner("Sedang melukis gambar Anda... Mohon tunggu..."):
                try:
                    # Menggunakan model khusus pembuat gambar milik Google
                    imagen_model = genai.GenerativeModel("imagen-3.0-generate-002")
                    result = imagen_model.generate_content(prompt_gambar)
                    
                    # Ambil gambar dari output biner
                    for part in result.candidates[0].content.parts:
                        if part.inline_data:
                            img_bytes = part.inline_data.data
                            generated_img = Image.open(io.BytesIO(img_bytes))
                            
                            st.image(generated_img, caption="Hasil Generate AI", use_container_width=True)
                            
                            # Tombol Download Gambar
                            buf = io.BytesIO()
                            generated_img.save(buf, format="PNG")
                            st.download_button(
                                label="Download Gambar (PNG)",
                                data=buf.getvalue(),
                                file_name="ai_generated_image.png",
                                mime="image/png"
                            )
                except Exception as e:
                    st.error(f"Gagal generate gambar. Pastikan kuota API Anda mencukupi atau coba model lain. Error: {e}")
        else:
            st.warning("Masukkan deskripsi gambar terlebih dahulu!")

# ==========================================
# TAB 3: GENERATOR FILE (DOWNLOAD OUTPUT)
# ==========================================
with tab3:
    st.subheader("📂 Buat Dokumen, Kode, atau Data Otomatis")
    st.write("Minta AI membuatkan data (CSV, TXT, HTML) dan Anda bisa langsung mendownload filenya.")
    
    opsi_file = st.selectbox("Pilih Format File yang Ingin Dibuat:", ["Text (.txt)", "Data/Excel (.csv)", "Script Python (.py)"])
    prompt_file = st.text_input("Deskripsikan isi file yang Anda butuhkan:", placeholder="Contoh: Buatkan tabel data 10 penjualan buah fiktif lengkap dengan harga")
    
    if st.button("Generate File"):
        if prompt_file:
            with st.spinner("Sedang memproses dokumen Anda..."):
                try:
                    model = genai.GenerativeModel(model_opsi)
                    instruksi = f"Buatkan konten murni untuk format {opsi_file} tanpa tambahan penjelasan teks pembuka atau penutup di luar isi file utama. Berikut adalah permintaannya: {prompt_file}"
                    response = model.generate_content(instruksi)
                    
                    konten_file = response.text
                    st.text_area("Preview Isi File:", konten_file, height=200)
                    
                    # Setup ekstensi file
                    ekstensi = ".txt" if "Text" in opsi_file else (".csv" if "Data" in opsi_file else ".py")
                    mime_type = "text/plain" if "Text" in opsi_file else ("text/csv" if "Data" in opsi_file else "text/x-python")
                    
                    st.download_button(
                        label=f"Download File {ekstensi}",
                        data=konten_file,
                        file_name=f"ai_generated_file{ekstensi}",
                        mime=mime_type
                    )
                except Exception as e:
                    st.error(f"Gagal membuat file: {e}")