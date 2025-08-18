import streamlit as st
import requests
import hashlib
import whisper
from pydub import AudioSegment
import tempfile

API = "http://127.0.0.1:8000"

left, center, right = st.columns([1, 4, 1])

with center:
    st.header("Text Summurizer")

lang_map = {
    "English": None,
    "Hindi": "hin_Deva",
    "Gujarati": "guj_Gujr",
    "French": "fra_Latn",
    "German": "deu_Latn"
}

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
        file_content = file.read().decode()
        file_name = file.name
        selected_lang = st.radio("Change Language:", list(lang_map.keys()))
        file_hash = hashlib.md5(file_content.encode()).hexdigest()

        if ("file_hash" not in st.session_state) or (st.session_state["file_hash"] != file_hash):
            if st.button("Generate text"):
                res = requests.post(f"{API}/upload", json = {
                    "file_name" : file_name,
                    "file_content" : file_content
                })
                if res.status_code == 200:
                    st.session_state["file_id"] = res.json()["file_id"]
                    st.session_state["file_hash"] = file_hash
                    res = requests.post(f"{API}/Generatetext", json = {
                    "file_id" : st.session_state["file_id"]
                    })
                    if res.status_code == 200:
                        summary = res.json().get("summary", "")
                    else:
                        st.error("Failed to generate text.")
                    # st.success("file Uploaded.")
                    if selected_lang == "English":
                        st.subheader("📝 Generated Summary:")
                        st.text_area("Summary Output", summary, height=200)
                        req = requests.post(f"{API}/upload_summury", json = {
                            "id" : st.session_state["file_id"],
                            "file_content" : summary,
                            "content_language" : selected_lang
                        })
                    else:
                        res = requests.post(f"{API}/changelanguage", json = {
                            "file_content" : summary,
                            "file_langauge" : lang_map[selected_lang]
                        })
                        if res.status_code == 200:
                            summary = res.json().get("summary", "")
                            st.subheader("📝 Generated Summary:")
                            st.text_area("Summary Output", summary, height=200)
                            req = requests.post(f"{API}/upload_summury", json = {
                            "id" : st.session_state["file_id"],
                            "file_content" : summary,
                            "content_language" : selected_lang})
                        else:
                            st.error("Failed to change!")
                else:
                    st.error("Couldn't handle file please reupload it!")
else:
    Audio = st.file_uploader(
        "Drag and drop a Audio here or click to browse",
        type = [".wav",".mp3",".m4a",".flac",".ogg",".opus",".aac",".wma"],
        help = "Only Video or Image files allowed",
        label_visibility = "collapsed"
    )
    if Audio:
        model = whisper.load_model("tiny")
        if Audio is not None:
            sound = AudioSegment.from_file(Audio)
            raw_data = sound.raw_data
            file_hash = hashlib.md5(raw_data).hexdigest()

        if ("file_hash" not in st.session_state) or (st.session_state["file_hash"] != file_hash):
            # Save to a temporary file in a format Whisper likes
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                temp_path = tmp_file.name
                sound.set_frame_rate(16000).set_channels(1).export(temp_path, format="wav")

            # Now transcribe safely
            result = model.transcribe(temp_path)
            text = result["text"]
            res = requests.post(f"{API}/upload", json = {
                "file_name" : Audio.name,
                "file_content" : text
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
                req = requests.post(f"{API}/upload_summury", json = {
                    "file_id" : st.session_state["file_id"],
                    "file_content" : summary
                })
                input = st.radio("Select Language: ", ["English", "Hindi", "Gujarati", "Franch", "Germen"])
                if input == "Germen":
                    res = requests.post(f"{API}/changelanguage", json = {
                        "file_content" : summary,
                        "file_langauge" : "deu_Latn"
                    })
                    if res.status_code == 200:
                        ans = res.json().get("")
                        st.subheader("📝 Generated Summary:")
                        st.text_area("Summary Output", ans, height=200)
                elif input == "Hindi":
                    res = requests.post(f"{API}/changelanguage", json = {
                        "file_content" : summary,
                        "file_langauge" : "hin_Deva"
                    })
                    if res.status_code == 200:
                        ans = res.json().get("")
                        st.subheader("📝 Generated Summary:")
                        st.text_area("Summary Output", ans, height=200)
                elif input == "Gujarati":
                    res = requests.post(f"{API}/changelanguage", json = {
                        "file_content" : summary,
                        "file_langauge" : "guj_Gujr"
                    })
                    if res.status_code == 200:
                        ans = res.json().get("")
                        st.subheader("📝 Generated Summary:")
                        st.text_area("Summary Output", ans, height=200)
                elif input == "Franch":
                    res = requests.post(f"{API}/changelanguage", json = {
                        "file_content" : summary,
                        "file_langauge" : "fra_Latn"
                    })
                    if res.status_code == 200:
                        ans = res.json().get("")
                        st.subheader("📝 Generated Summary:")
                        st.text_area("Summary Output", ans, height=200)
                else:
                    st.subheader("📝 Generated Summary:")
                    st.text_area("Summary Output", summary, height=200)
            else:
                st.error("Failed to generate text.")