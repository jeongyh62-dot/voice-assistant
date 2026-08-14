# --------------------------------------------------
# 필요한 라이브러리 불러오기
# --------------------------------------------------

import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import tempfile
import os


# --------------------------------------------------
# 1. 기본 화면 설정
# --------------------------------------------------

st.set_page_config(
    page_title="솔로몬의 지혜",
    page_icon="👑",
    layout="wide"
)

st.markdown(
    """
    <style>

    /* 전체 기본 글자 크기 */
    html, body, [class*="css"] {
        font-size: 18px;
    }

    /* 일반 설명 글자 */
    .stMarkdown, .stText, p, label {
        font-size: 18px !important;
    }

    /* 입력창 글자 */
    textarea, input {
        font-size: 18px !important;
    }

    /* 버튼 글자 */
    .stButton button {
        font-size: 18px !important;
    }
        /* 라디오 버튼 글자 */
    div[role="radiogroup"] label {
        font-size: 18px !important;
    }

    /* 사이드바 글자 */
    section[data-testid="stSidebar"] {
        font-size: 18px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 2. 왼쪽 Sidebar 구성
# --------------------------------------------------

try:
    st.sidebar.image(
        "solomon.png",
        caption="지혜의 왕 솔로몬",
        use_container_width=True
    )
except Exception:
    st.sidebar.info(
        "📷 solomon.png 이미지를 app.py와 같은 폴더에 넣어주세요."
    )

st.sidebar.title("👑 솔로몬의 지혜")

st.sidebar.write(
    "텍스트 또는 음성으로 질문하면 Gemini가 답변하고, "
    "답변을 음성으로 들려주는 AI 지혜 비서입니다."
)

st.sidebar.markdown("---")


# --------------------------------------------------
# 3. Gemini API Key 입력
# --------------------------------------------------

st.sidebar.subheader("🔑 Gemini API 설정")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    placeholder="본인의 Gemini API Key를 입력하세요"
)

st.sidebar.caption(
    "API Key가 없다면 아래 버튼을 눌러 Google AI Studio에서 발급받으세요."
)

st.sidebar.link_button(
    "🔗 Gemini API Key 발급받기",
    "https://aistudio.google.com/app/apikey",
    use_container_width=True
)


# --------------------------------------------------
# 4. 채팅 기록 초기화
# --------------------------------------------------

if "chat" not in st.session_state:
    st.session_state.chat = []

# --------------------------------------------------
# 5. 메인 화면 제목
# --------------------------------------------------

st.title("👑 솔로몬의 지혜")

st.caption(
    "텍스트로 질문하거나, 마이크 버튼을 눌러 음성으로 질문해 보세요."
)

st.markdown("---")


# --------------------------------------------------
# 6. 입력 방법 선택
# --------------------------------------------------

input_mode = st.radio(
    "질문 입력 방법을 선택하세요",
    ["⌨️ 텍스트 입력", "🎤 음성 입력"],
    horizontal=True
)


# --------------------------------------------------
# 7. 화면을 두 개의 열로 구성
# --------------------------------------------------

col1, col2 = st.columns([1, 1])


# --------------------------------------------------
# 8. 질문 입력 영역
# --------------------------------------------------

with col1:
    st.subheader("💬 솔로몬에게 질문하기")

    question = ""
    ask_button = False
    audio_value = None

    if input_mode == "⌨️ 텍스트 입력":

        question = st.text_area(
            "질문을 입력하세요",
            placeholder="예: 인생에서 가장 중요한 것은 무엇인가요?",
            height=150,
            key="text_question_input"
        )

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            ask_button = st.button(
                "✨ 지혜 구하기",
                use_container_width=True,
                type="primary",
                key="text_ask_button"
            )

        with btn_col2:
            if st.button(
                "🗑️ 대화 초기화",
                use_container_width=True,
                key="text_reset_button"
            ):
                st.session_state.chat = []
                st.rerun()
                
        
    else:
        audio_value = st.audio_input(
            "🎤 마이크를 눌러 질문을 말씀해 주세요",
            sample_rate=16000,
            key="voice_audio_input"
        )

        if audio_value:
            st.audio(audio_value)

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            ask_button = st.button(
                "🎙️ 음성 질문 보내기",
                use_container_width=True,
                type="primary",
                key="voice_ask_button"
            )

        with btn_col2:
            if st.button(
                "🗑️ 대화 초기화",
                use_container_width=True,
                key="voice_reset_button"
            ):
                st.session_state.chat = []
                st.rerun()


# --------------------------------------------------
# 9. 질문 / 답변 영역 제목
# --------------------------------------------------

with col2:
    st.subheader("📜 질문 / 답변")


# --------------------------------------------------
# 10. 질문 보내기 버튼을 눌렀을 때 처리
# --------------------------------------------------

if ask_button:

    if not api_key:
        st.warning(
            "Gemini API Key를 먼저 입력해 주세요."
        )

    else:
        try:
            client = genai.Client(
                api_key=api_key
            )

            # 텍스트 질문 처리
            if input_mode == "⌨️ 텍스트 입력":

                if not question.strip():
                    st.warning(
                        "솔로몬에게 질문할 내용을 입력해 주세요."
                    )
                else:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=question
                    )

                    answer = response.text

            # 음성 질문 처리
            else:

                if audio_value is None:
                    st.warning(
                        "먼저 마이크 버튼을 눌러 질문을 녹음해 주세요."
                    )
                    question = ""
                    answer = ""

                else:
                    audio_bytes = audio_value.getvalue()

                    # 1단계: 음성을 텍스트 질문으로 변환
                    transcription_response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=[
                            "다음 한국어 음성을 정확히 받아쓰기만 해주세요. "
                            "설명이나 답변은 하지 말고, 사용자가 말한 문장만 출력하세요.",
                            types.Part.from_bytes(
                                data=audio_bytes,
                                mime_type="audio/wav"
                            )
                        ]
                    )

                    question = transcription_response.text.strip()

                    st.success(
                        f"🎤 인식된 질문: {question}"
                    )

                    # 2단계: 인식된 질문에 답변 생성
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=question
                    )

                    answer = response.text

            # 질문과 답변 저장
            if question and answer:

                st.session_state.chat.append(
                    ("사용자", question)
                )

                st.session_state.chat.append(
                    ("솔로몬", answer)
                )

                # 답변을 음성으로 변환
                tts = gTTS(
                    text=answer,
                    lang="ko"
                )

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3"
                ) as fp:
                    audio_path = fp.name

                tts.save(
                    audio_path
                )

                # 음성 재생
                st.audio(
                    audio_path,
                    format="audio/mp3",
                    autoplay=True
                )

                os.remove(
                    audio_path
                )

        except Exception as e:
            st.error(
                f"오류가 발생했습니다: {e}"
            )


# --------------------------------------------------
# 11. 저장된 질문과 답변을 오른쪽 화면에 표시
# --------------------------------------------------

with col2:

    for sender, message in st.session_state.chat:

        if sender == "사용자":
            st.markdown(
                f"**👤 사용자**  \n{message}"
            )
        else:
            st.markdown(
                f"**👑 솔로몬의 지혜**  \n{message}"
            )

        st.markdown("---")


# --------------------------------------------------
# 12. Sidebar 하단 보안 안내
# --------------------------------------------------

st.sidebar.markdown("---")

st.sidebar.caption(
    "※ API Key는 입력창에서만 사용되며 app.py 코드에 저장되지 않습니다."
)
