import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Türkçe Akıllı Öğrenci Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Türkçe Akıllı Öğrenci Asistanı")
st.caption("🚀 Yapay Zekâ ve Web Entegrasyonlu Akademik Karar Destek Sistemi")

SYSTEM_INSTRUCTION = """
Sen üniversite öğrencilerine rehberlik eden, yapay zekâ destekli 'Türkçe Akıllı Öğrenci Asistanı'sın.
Görevin, öğrencilerin ders seçimi, ders çalışma stratejileri, akademik başarı, zaman yönetimi ve motivasyonla ilgili sorularını yanıtlamaktır.
Yanıtların her zaman samimi, yapıcı, yönlendirici ve akademik olarak tutarlı olmalıdır.
Eğer öğrenci belirli bir ders ismi verirse, o dersin zorluk derecesini, çalışma yöntemlerini ve eğer gerekli ise ön koşul derslerini mantıksal analiz ederek anlat.
"""

# API key'i Streamlit Secrets'tan oku
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API key bulunamadı. Streamlit Cloud → Settings → Secrets bölümüne GEMINI_API_KEY ekleyin.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben senin akademik asistanınım. Ders seçimi, sınav taktikleri veya üniversite hayatı hakkında bana ne danışmak istersin?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Mesajınızı buraya yazın..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    try:
        client = genai.Client(api_key=api_key)
        contents = []

        for msg in st.session_state.messages[:-1]:
            role_type = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role_type, parts=[types.Part.from_text(text=msg["content"])]))

        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_query)]))

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Düşünüyorum..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7
                    )
                )
            response_placeholder.markdown(response.text)

        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"Bir hata oluştu: {str(e)}")