import streamlit as st
import time

st.title("AutoAccept テスト用画面")
st.write("この画面は、自動承認ツールが正しくボタンを検知できるかテストするためのものです。")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Accept"):
        st.success("Accept が押されました！")

with col2:
    if st.button("Accept All"):
        st.success("Accept All が押されました！")

with col3:
    if st.button("Accept Change"):
        st.success("Accept Change が押されました！")

st.markdown("---")
if st.button("Accept Alt (Secret)"):
    st.warning("Accept Alt が押されました！")
