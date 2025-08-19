import streamlit as st
from services import textfilehandler, Audiofilehandler

left, center, right = st.columns([1, 4, 1])
with center:
    st.header("Text Summurizer")

st.title("📂 Choose Input Type")
input_type = st.radio("Select input type:", ["PDF", "Audio"])

if input_type == "PDF":
    file = st.file_uploader(
    "Drag and drop a file here or click to browse",
    type=["pdf", "txt", "text"],
    help="Only PDF or TXT files allowed",
    label_visibility= "collapsed"  # Hide label to look cleaner like a dropzone
    )

    if file:
        textfilehandler.textfilehandler(file)
else:
    Audio = st.file_uploader(
        "Drag and drop a Audio here or click to browse",
        type = [".wav",".mp3",".m4a",".flac",".ogg",".opus",".aac",".wma"],
        help = "Only Video or Image files allowed",
        label_visibility = "collapsed"
    )
    if Audio:
        Audiofilehandler.audiohandler(Audio)