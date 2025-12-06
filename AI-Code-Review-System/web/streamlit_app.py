import streamlit as st
import requests

st.title("AI Code Review Assistant — Simple Prototype")

code = st.text_area("Paste your code here", height=300)
lang = st.selectbox("Language", ["python", "javascript"])

if st.button("Run Review"):
    if not code.strip():
        st.warning("Please paste some code before running the review.")
    else:
        try:
            resp = requests.post("http://127.0.0.1:8000/review", json={"code": code, "language": lang})
            if resp.status_code != 200:
                st.error(f"API error: {resp.status_code} - {resp.text}")
            else:
                data = resp.json()
                st.success(data.get("summary", "Review completed"))
                for iss in data.get("issues", []):
                    st.subheader(f"{iss.get('id')} — {iss.get('severity')}")
                    st.write(iss.get("message"))
                    if iss.get("suggested_fix"):
                        st.code(iss.get("suggested_fix"))
                    if iss.get("explanation"):
                        st.write(iss.get("explanation"))
        except Exception as e:
            st.error(f"Failed to call API: {e}")
