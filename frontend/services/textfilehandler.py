import streamlit as st
import hashlib
import requests
from utils import languagemap, api

lang_map = languagemap.lang_map
API = api.API


def textfilehandler(file):
    file_content = file.read().decode()
    file_name = file.name
    file_hash = hashlib.md5(file_content.encode()).hexdigest()

    if ("file_hash" not in st.session_state) or (st.session_state["file_hash"] != file_hash):
        if st.button("Generate text"):
            res = requests.post(f"{API}/api/upload", json = {
                "file_name" : file_name,
                "file_content" : file_content
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
                # st.success("file Uploaded.")
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