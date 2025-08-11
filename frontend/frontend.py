import streamlit as st
import requests
import hashlib

API = "http://127.0.0.1:8000"

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
        file_content = file.read().decode()
        file_name = file.name

        file_hash = hashlib.md5(file_content.encode()).hexdigest()

        if ("file_hash" not in st.session_state) or (st.session_state["file_hash"] != file_hash):
            res = requests.post(f"{API}/upload", json = {
                "file_name" : file_name,
                "file_content" : file_content
            })

            if res.status_code == 200:
                st.session_state["file_id"] = res.json()["file_id"]
                st.session_state["file_hash"] = file_hash
                st.success("file Uploaded.")
            else:
                st.error("Couldn't handle file please reupload it!")

        if st.button("Generate summary") and "file_id" in st.session_state:
            res = requests.post(f"{API}/Generatetext", json = {
                "file_id" : st.session_state["file_id"]
            })

            if res.status_code == 200:
                summary = res.json().get("summary", "")
                st.subheader("📝 Generated Summary:")
                st.text_area("Summary Output", summary, height=200)
            else:
                st.error("Failed to generate text.")
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