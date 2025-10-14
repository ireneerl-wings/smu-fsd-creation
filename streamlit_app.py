import streamlit as st
import app as backend
import os
import streamlit_pdf_viewer as st_pdf_viewer

st.set_page_config(page_title="FSD Chatbot", page_icon="🌐", layout="wide")

# --- Mapping FSD ke file txt & PDF ---
FSD_MAPPING = {
    "A0001 - Enhancement for Custom Contract and Custom Order Unit in Purchase Order with Contract": {
        "txt": r"Txt\436109344_requirements3 (1).md",
        "pdf": r"Pdf\SD1-A0001 - Custom Contract and Custom Order Unit in Purchase Order with Contract-140825-162547.pdf"
    },
    "B0141 - Auto Delete Reservation enhancement for SAP system": {
        "txt": r"Txt\413008086_requirements3.md",
        "pdf": r"Pdf\B0141\SD1-B0141 - Auto Delete Reservation-140825-161854.pdf"
    },
    "C0177 - Weighing Machine at BS for GI & GR based on CO PRO - Connect to Weighing Machine from Fiori - SAP S/4": {
        "txt": r"Txt\434077697_requirements3.md",
        "pdf": r"Pdf\C0177.pdf"
    },
    "C0338 - OUT I/F to provide detail stock in Storage Bin - SAP S/4": {
        "txt": r"Txt\466681857_requirements3.md",
        "pdf": r"Pdf\C0338.pdf"
    },
    "D0091 - Inbound interface from satellite Apps to create SO - SFA - API - SAP S/4": {
        "txt": r"Txt\484147232_requirements3.md",
        "pdf": r"Pdf\D0091.pdf"
    },
    "E0067 - (LM) POD (Proof Of Delivery) DELMAN to SAP S4": {
        "txt": r"Txt\445579749_requirements3 (1).md",
        "pdf": r"Pdf\SD1-E0067- (LM) POD (Proof Of Delivery) DELMAN to SAP S4-140825-162433.pdf"
    }
}

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "txt_path" not in st.session_state:
    st.session_state.txt_path = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = backend.get_session_id()

def display_pdf(pdf_file):
    if not os.path.exists(pdf_file):
        st.error(f"❌ File PDF tidak ditemukan: {pdf_file}")
        return
    try:
        with open(pdf_file, "rb") as f:
            # Tidak perlu encode ke base64, cukup baca filenya
            st_pdf_viewer.pdf_viewer(f.read(), height=600)
    except Exception as e:
        st.error(f"⚠️ Gagal membuka PDF: {e}")


with st.sidebar:
    title_col, reset_col = st.columns([2.5, 1])

    with title_col:
        st.markdown("### 📂 Pilih FSD File")

    with reset_col:
        if st.button("🔄 Reset"):
            st.session_state.chat_history = []
            st.session_state.pdf_path = None
            st.session_state.txt_path = None
            st.rerun()

    fsd_options = list(FSD_MAPPING.keys())
    selected_fsd_display = st.selectbox(
        "FSD:", 
        options=fsd_options,
        format_func=lambda x: f"{x[:50]}..." if len(x) > 50 else x,
        label_visibility="collapsed" 
    )
    
    if st.button("Submit", use_container_width=True):
        st.session_state.txt_path = FSD_MAPPING[selected_fsd_display]["txt"]
        st.session_state.pdf_path = FSD_MAPPING[selected_fsd_display]["pdf"]

    if st.session_state.pdf_path:
        st.markdown("---") 
        st.markdown("### 📑 Preview FSD PDF")
        display_pdf(st.session_state.pdf_path)



# with st.sidebar:
#     st.markdown("### 📂 Pilih FSD File")

#     # Ambil daftar FSD dan potong jika terlalu panjang untuk ditampilkan di selectbox
#     fsd_options = list(FSD_MAPPING.keys())
#     selected_fsd_display = st.selectbox(
#         "FSD:", 
#         options=fsd_options,
#         format_func=lambda x: f"{x[:50]}..." if len(x) > 50 else x # Potong teks panjang
#     )
    
#     # Tombol Submit
#     if st.button("✅ Submit"):
#         # Simpan path file yang dipilih ke session_state
#         st.session_state.txt_path = FSD_MAPPING[selected_fsd_display]["txt"]
#         st.session_state.pdf_path = FSD_MAPPING[selected_fsd_display]["pdf"]

#     # Tombol Reset
#     if st.button("🔄 Reset Session"):
#         backend.clear_session()
#         # Reset semua state yang relevan
#         st.session_state.chat_history = []
#         st.session_state.session_id = backend.get_session_id()
#         st.session_state.pdf_path = None
#         st.session_state.txt_path = None
#         st.rerun()

#     # Tampilkan PDF JIKA path-nya sudah tersimpan di session_state
#     if st.session_state.pdf_path:
#         st.markdown("---") # Garis pemisah
#         st.markdown("### 📑 Preview FSD PDF")
#         display_pdf(st.session_state.pdf_path)

# ---------------- Main Area (Chat) ----------------
st.title("🌐 FSD Chatbot")

# Riwayat obrolan
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input pengguna
user_input = st.chat_input("Tanyakan apa saja seputar FSD yang dipilih...")

if user_input:
    if not st.session_state.txt_path:
        st.warning("⚠️ Silakan pilih FSD dan klik 'Submit' terlebih dahulu.")
    else:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("⏳ Sedang memproses..."):
            try:
                response = backend.process_streamlit(
                    user_input, 
                    st.session_state.session_id, 
                    st.session_state.txt_path 
                )
            except Exception as e:
                response = f"❌ Terjadi kesalahan saat memproses pertanyaan: {e}"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# streamlit run "D:\Linneke\Proyek Req Trace AI\code_chatbot\streamlit_app.py"