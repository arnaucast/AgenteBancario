
import streamlit as st
import whisper
import numpy as np
st.write("Cargando modelo Whisper...")
model = whisper.load_model("base")
st.write("Modelo cargado con éxito")