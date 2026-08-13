import streamlit as st
from google import genai
from gtts import gTTS
import tempfile
import os

# ------------------------------------
# 기본 화면 설정
# ------------------------------------
st.set_page_config(
    page_title="Gemini 음성비서",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Gemini 음성비서 프로그램")
st.markdown("---")

with st.expander("음성비서 프로그램에 관하여", expanded=True):
    st.write("""
    - UI는 Streamlit을 활용하여 만들었습니다.
    - 답변 생성에는 Google Gemini API를 사용합니다.
    - TTS(Text-To-Speech)는 gTTS를 사용합니다.
    """)

# ------------------------------------
# API Key 입력
# ------------------------------------
st.sidebar.header("설정")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    placeholder="본인의 Gemini API Key를 입력하세요"
)

# ------------------------------------
# 채팅 기록 초기화
# ------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ------------------------------------
# 화면 2열 구성
# ------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("질문하기")

    question = st.text_area(
        "Gemini에게 질문하세요",
        placeholder="예: 오늘 저녁 메뉴를 추천해 주세요."
    )

    ask_button = st.button(
        "질문하기",
        use_container_width=True
    )

with col2:
    st.subheader("질문 / 답변")

# ------------------------------------
# Gemini 질문
# ------------------------------------
if ask_button:

    if not api_key:
        st.warning("Gemini API Key를 입력해 주세요.")

    elif not question.strip():
        st.warning("질문을 입력해 주세요.")

    else:
        try:
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=question
            )

            answer = response.text

            # 대화 저장
            st.session_state.chat.append(
                ("사용자", question)
            )
            st.session_state.chat.append(
                ("Gemini", answer)
            )

            # -------------------------
            # 답변 → 음성
            # -------------------------
            tts = gTTS(
                text=answer,
                lang="ko"
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            ) as fp:

                audio_path = fp.name

            tts.save(audio_path)

            # 음성 재생
            st.audio(
                audio_path,
                format="audio/mp3",
                autoplay=True
            )

            os.remove(audio_path)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# ------------------------------------
# 채팅 화면
# ------------------------------------
with col2:

    for sender, message in st.session_state.chat:

        if sender == "사용자":
            st.markdown(f"**👤 사용자**  \n{message}")

        else:
            st.markdown(f"**🤖 Gemini**  \n{message}")

        st.markdown("---")

# ------------------------------------
# 초기화
# ------------------------------------
if st.sidebar.button("대화 초기화"):

    st.session_state.chat = []
    st.rerun()