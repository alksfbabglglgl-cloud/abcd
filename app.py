import streamlit as st

st.title("안녕하세요! 👋")
st.write("이것은 아주 쉬운 Streamlit 예제입니다!")

name = st.text_input("이름을 입력해 보세요:")

if name:
    st.success(f"{name}님 환영합니다! 🎉")
