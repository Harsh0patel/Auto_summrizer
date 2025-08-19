import streamlit as st
import whisper
from pydub import AudioSegment
import hashlib
import tempfile
import requests
from utils import api, languagemap

API = api.API
lang_map = languagemap.lang_map

@st.cache_resource
def load_model():
    return whisper.load_model("tiny")


def audiohandler(Audio):
    model = load_model()
    if Audio is not None:
        sound = AudioSegment.from_file(Audio)
        raw_data = sound.raw_data
        file_hash = hashlib.md5(raw_data).hexdigest()

    if ("file_hash" not in st.session_state) or (st.session_state["file_hash"] != file_hash):
        if st.button("Generate text"):
            # Save to a temporary file in a format Whisper likes
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                temp_path = tmp_file.name
                sound.set_frame_rate(16000).set_channels(1).export(temp_path, format="wav")

            # Now transcribe safely
            result = model.transcribe(temp_path)
            text = result["text"]
            res = requests.post(f"{API}/api/upload", json = {
                "file_name" : Audio.name,
                "file_content" : text
            })

            if res.status_code == 200:
                st.session_state["file_id"] = res.json()["file_id"]
                st.session_state["file_hash"] = file_hash
                res = requests.post(f"{API}/api/Generatetext", json = {
                "file_id" : st.session_state["file_id"]
                })
                if res.status_code == 200:
                    summary = res.json().get("summary", "")
                    req = requests.post(f"{API}/api/upload_summury", json = {
                        "id" : st.session_state["file_id"],
                        "file_content" : summary,
                    })
                    if req.status_code == 200:
                        pass
                    else:
                        st.error("File Upload error.")
                    st.subheader("📝 Generated Summary:")
                    st.text_area("Summary Output", summary, height=200)
                else:
                    st.error("Failed to generate text.")
            else:
                st.error("Couldn't handle file please reupload it!")

    if ("file_hash" in st.session_state):
        selected_lang = st.radio("Change Language:", list(lang_map.keys()))
        if st.button("Change Language") and selected_lang:
                res = requests.post(f"{API}/api/changelanguage", json = {
                    "id" : st.session_state["file_id"],
                    "language" : lang_map[selected_lang]
                })
                if res.status_code == 200:
                    summary = res.json().get("summary", "")
                    st.subheader("📝 Generated Summary:")
                    st.text_area("Summary Output", summary, height=200)
                else:
                    st.error("Fail to process data, try again.")