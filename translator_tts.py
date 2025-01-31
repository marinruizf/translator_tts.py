import os
import openai
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
import speech_recognition as sr

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ Error: La clave API no está configurada. Verifica tu archivo .env.")
    st.stop()

# Configure OpenAI API
openai.api_key = api_key

# Configure Streamlit interface
st.set_page_config(page_title="AI Translation + TTS + STT", page_icon="🌍")
st.title("🌍 AI Translation + TTS + STT")
st.write("Ingrese texto, seleccione un idioma para traducir y escuchar, o hable para traducir.")

# User input
text = st.text_area("Ingrese texto:", "")
language = st.selectbox("Seleccione idioma:", ["es", "fr", "de", "it", "pt", "zh", "ja"])

# Initialize session state for recognized text
if 'recognized_text' not in st.session_state:
    st.session_state.recognized_text = ""

# Speech-to-Text functionality
st.write("O hable para traducir:")
if st.button("Grabar Audio"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Hable ahora...")
        audio = recognizer.listen(source, timeout=10)  # Increase timeout to 10 seconds
        st.write("🎤 Grabación finalizada.")
        
        try:
            # Recognize speech using Google Web Speech API
            st.session_state.recognized_text = recognizer.recognize_google(audio, language='es-ES')  # Change language as needed
            st.success(f"Texto reconocido: {st.session_state.recognized_text}")
        except sr.UnknownValueError:
            st.error("❌ No se pudo entender el audio.")
        except sr.RequestError as e:
            st.error(f"❌ Error al solicitar resultados de Google Speech Recognition; {e}")

# Use the recognized text for translation
if st.button("Traducir"):
    # Use recognized text if available, otherwise use entered text
    translation_text = st.session_state.recognized_text if st.session_state.recognized_text.strip() else text

    if not translation_text.strip():
        st.warning("⚠ Debes ingresar un texto para traducir.")
    else:
        try:
            # Call OpenAI API for translation
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un traductor profesional."},
                    {"role": "user", "content": f"Translate this to {language}: {translation_text}"}
                ]
            )

            translation = response["choices"][0]["message"]["content"]
            st.success("✅ Traducción completada:")
            st.write(translation)

            # Text-to-Speech using gTTS
            tts = gTTS(text=translation, lang=language)
            audio_file = "output.mp3"
            tts.save(audio_file)

            # Play the audio file directly in the app
            st.audio(audio_file)

        except Exception as e:
            st.error(f"❌ Error: {e}")
