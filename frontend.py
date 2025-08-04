import streamlit as st
import backend
import io
import spacy
import subprocess
import sys


@st.cache_resource
def load_model_temporarily():
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        st.write("Downloading temporary spaCy model...")
        
        # Download the model
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

left, center, right = st.columns([1, 4, 1])

with center:
    st.header("Text Summurizer")

st.title("📂 Choose Input Type")
input_type = st.radio("Select input type:", ["PDF", "Video"])

if input_type == "PDF":
    file = st.file_uploader(
    "Drag and drop a file here or click to browse",
    type=["pdf", "txt", "text"],
    help="Only PDF or TXT files allowed",
    label_visibility= "collapsed"  # Hide label to look cleaner like a dropzone
    )

    if file:
        st.success(f"PDF Uploaded: {file.name}")
        file = io.BytesIO(file.read())
        # st.write(file.read())
        # Placeholder for actual PDF processing
        # Replace with your own logic
        obj = backend.Parser()
        summary_text = obj.parse_file(file)
        
        # Display summary
        st.subheader("📝 Generated Summary:")
        st.text_area("Summary Output", summary_text, height=200)
else:
    video = st.file_uploader(
        "Drag and drop a video here or click to browse",
        type = [".mp4", ".jpeg", ".png"],
        help = "Only Video or Image files allowed",
        label_visibility = "collapsed"
    )
    if video:
        st.success(f"PDF Uploaded: {video.name}")
        
        # Placeholder for actual PDF processing
        # Replace with your own logic
        summary_text = "This is a dummy summary of the uploaded PDF."
        
        # Display summary
        st.subheader("📝 Generated Summary:")
        st.text_area("Summary Output", summary_text, height=200)
