import streamlit as st
import hashlib
import requests
import whisper
from pydub import AudioSegment
import tempfile

# Page configuration
st.set_page_config(
    page_title="AI Text Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API = "http://161.118.190.255:8000"

# Language mapping
lang_map = {
    "English": None,
    "Hindi": "hin_Deva",
    "Gujarati": "guj_Gujr",
    "French": "fra_Latn",
    "German": "deu_Latn"
}

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .step-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 2rem 0;
        border: 1px solid #e1e8ed;
    }
    
    .step-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .upload-zone {
        border: 3px dashed #bdc3c7;
        border-radius: 15px;
        padding: 3rem 2rem;
        text-align: center;
        background: #fafbfc;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    .upload-zone.has-file {
        border-color: #27ae60;
        background: #f8fff9;
    }
    
    .status-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 4px solid;
    }
    
    .status-success {
        background: #f8fff9;
        border-left-color: #27ae60;
        color: #27ae60;
    }
    
    .status-info {
        background: #f8f9ff;
        border-left-color: #3498db;
        color: #2980b9;
    }
    
    .status-error {
        background: #fff5f5;
        border-left-color: #e53e3e;
        color: #e53e3e;
    }
    
    .progress-steps {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .progress-step.completed {
        background: #27ae60;
        color: white;
    }
    
    .progress-step.active {
        background: #667eea;
        color: white;
    }
    
    .progress-step.pending {
        background: #ecf0f1;
        color: #7f8c8d;
    }
    
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e1e8ed, transparent);
        margin: 3rem 0;
    }

    .summary-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e1e8ed;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load Whisper model for audio processing
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")

# Text file handler
def handle_text_file(file):
    """Handle text/PDF file processing"""
    file_content = file.read().decode("utf-8", errors = "replace")
    file_name = file.name
    file_hash = hashlib.md5(file_content.encode()).hexdigest()

    if ("file_hash" not in st.session_state) or (st.session_state["file_hash"] != file_hash):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Summary", use_container_width=True, type="primary"):
                with st.spinner("Processing your document..."):
                    try:
                        # Upload file to API
                        res = requests.post(f"{API}/api/upload", json={
                            "file_name": file_name,
                            "file_content": file_content
                        })
                        
                        if res.status_code == 200:
                            st.session_state["file_id"] = res.json()["file_id"]
                            st.session_state["file_hash"] = file_hash
                            
                            # Generate summary
                            res = requests.post(f"{API}/api/Generatetext", json={
                                "file_id": st.session_state["file_id"]
                            })
                            
                            if res.status_code == 200:
                                summary = res.json().get("summary", "")
                                
                                # Upload summary
                                req = requests.post(f"{API}/api/upload_summury", json={
                                    "id": st.session_state["file_id"],
                                    "file_content": summary,
                                })
                                
                                if req.status_code == 200:
                                    st.session_state["summary"] = summary
                                    st.session_state["current_step"] = 4
                                    st.success("✅ Summary generated successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to save summary. Please try again.")
                            else:
                                st.error("❌ Failed to generate summary. Please try again.")
                        else:
                            st.error("❌ Couldn't upload file. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Audio file handler
def handle_audio_file(audio_file):
    """Handle audio file processing"""
    model = load_whisper_model()
    
    if audio_file is not None:
        sound = AudioSegment.from_file(audio_file)
        raw_data = sound.raw_data
        file_hash = hashlib.md5(raw_data).hexdigest()

        if ("file_hash" not in st.session_state) or (st.session_state["file_hash"] != file_hash):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Transcribe & Summarize", use_container_width=True, type="primary"):
                    with st.spinner("Transcribing audio and generating summary..."):
                        try:
                            # Save to temporary file for Whisper
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                                temp_path = tmp_file.name
                                sound.set_frame_rate(16000).set_channels(1).export(temp_path, format="wav")

                            # Transcribe audio
                            result = model.transcribe(temp_path)
                            text = result["text"]
                            
                            # Upload transcribed text
                            res = requests.post(f"{API}/api/upload", json={
                                "file_name": audio_file.name,
                                "file_content": text
                            })

                            if res.status_code == 200:
                                st.session_state["file_id"] = res.json()["file_id"]
                                st.session_state["file_hash"] = file_hash
                                
                                # Generate summary
                                res = requests.post(f"{API}/api/Generatetext", json={
                                    "file_id": st.session_state["file_id"]
                                })
                                
                                if res.status_code == 200:
                                    summary = res.json().get("summary", "")
                                    
                                    # Upload summary
                                    req = requests.post(f"{API}/api/upload_summury", json={
                                        "id": st.session_state["file_id"],
                                        "file_content": summary,
                                    })
                                    
                                    if req.status_code == 200:
                                        st.session_state["summary"] = summary
                                        st.session_state["current_step"] = 4
                                        st.success("✅ Audio transcribed and summarized successfully!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to save summary.")
                                else:
                                    st.error("❌ Failed to generate summary.")
                            else:
                                st.error("❌ Couldn't process audio file. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

# Initialize session state
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "mode" not in st.session_state:
    st.session_state.mode = "PDF"
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "English"

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Text Summarizer</h1>
    <p>Transform your documents and audio into concise, meaningful summaries</p>
</div>
""", unsafe_allow_html=True)

# Progress steps removed for cleaner interface

# Step 1: Choose Input Type
st.markdown("""
<div class="step-container">
    <div class="step-header">
        📂 Choose Your Input Type
    </div>
</div>
""", unsafe_allow_html=True)

# Input type selection
col1, col2 = st.columns(2)

with col1:
    if st.button("📄 PDF / Text Documents", key="pdf_btn", use_container_width=True, 
                type="primary" if st.session_state.mode == "PDF" else "secondary"):
        st.session_state.mode = "PDF"
        st.session_state.current_step = max(st.session_state.current_step, 1)

with col2:
    if st.button("🎵 Audio Files", key="audio_btn", use_container_width=True,
                type="primary" if st.session_state.mode == "Audio" else "secondary"):
        st.session_state.mode = "Audio"
        st.session_state.current_step = max(st.session_state.current_step, 1)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# File Upload Section
st.markdown("""
<div class="step-container">
    <div class="step-header">
        📥 Upload Your File
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.mode == "PDF":
    st.markdown("**Supported formats:** PDF, TXT")
    file = st.file_uploader(
        "Choose your document",
        type=["pdf", "txt", "text"],
        help="Maximum file size: 200MB",
        key="text_uploader"
    )
    if file:
        file_size = len(file.read()) / (1024 * 1024)
        file.seek(0)
        st.markdown(f"""
        <div class="status-card status-success">
            <strong>✅ File uploaded successfully!</strong><br>
            📎 {file.name} ({file_size:.1f} MB)
        </div>
        """, unsafe_allow_html=True)
        st.session_state.current_step = max(st.session_state.current_step, 2)
        handle_text_file(file)
else:
    st.markdown("**Supported formats:** WAV, MP3, M4A, FLAC, OGG, OPUS, AAC, WMA")
    audio_file = st.file_uploader(
        "Choose your audio file",
        type=["wav", "mp3", "m4a", "flac", "ogg", "opus", "aac", "wma"],
        help="Maximum file size: 200MB",
        key="audio_uploader"
    )
    if audio_file:
        file_size = len(audio_file.read()) / (1024 * 1024)
        audio_file.seek(0)
        st.markdown(f"""
        <div class="status-card status-success">
            <strong>✅ Audio file uploaded successfully!</strong><br>
            🎵 {audio_file.name} ({file_size:.1f} MB)
        </div>
        """, unsafe_allow_html=True)
        st.session_state.current_step = max(st.session_state.current_step, 2)
        handle_audio_file(audio_file)

# Show language options and summary if file is processed
if "summary" in st.session_state and "file_hash" in st.session_state:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Language change section
    st.markdown("""
    <div class="step-container">
        <div class="step-header">
            🌍 Change Language (Optional)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_lang = st.selectbox("Select Language:", list(lang_map.keys()), key="lang_selector")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Change Language", use_container_width=True, type="secondary"):
            if selected_lang:
                with st.spinner(f"Translating to {selected_lang}..."):
                    try:
                        res = requests.post(f"{API}/api/changelanguage", json={
                            "id": st.session_state["file_id"],
                            "language": lang_map[selected_lang]
                        })
                        
                        if res.status_code == 200:
                            translated_summary = res.json().get("summary", "")
                            st.session_state["summary"] = translated_summary
                            st.session_state["selected_lang"] = selected_lang
                            st.success(f"✅ Summary translated to {selected_lang}!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to translate. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Translation error: {str(e)}")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Display summary at the bottom
    current_language = st.session_state.get("selected_lang", "English")
    
    st.markdown(f"""
    <div class="step-container">
        <div class="step-header">
            📋 Generated Summary ({current_language})
        </div>
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-top: 1rem;
        ">
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #2c3e50;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">
                <h5 style="color: #667eea; margin-bottom: 1rem; font-weight: 600;">📄 Summary Content:</h5>
                <p style="margin: 0; white-space: pre-wrap;">{st.session_state["summary"]}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Download and reset options
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Summary",
            st.session_state["summary"],
            file_name="ai_summary.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Process New File", use_container_width=True):
            # Reset session state
            for key in ["file_hash", "file_id", "summary"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_step = 1
            st.rerun()

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem 0; color: #7f8c8d; border-top: 1px solid #ecf0f1; margin-top: 3rem;">
    <p>Built with ❤️ using Streamlit • © 2025 Text Summarizer</p>
</div>
""", unsafe_allow_html=True)