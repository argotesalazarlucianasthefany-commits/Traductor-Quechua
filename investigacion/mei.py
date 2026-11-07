import streamlit as st
import os
import json

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://openrouter.ai/api/v1"
MODELO_FREE = "nvidia/nemotron-3-ultra-550b-a55b:free"

API_KEY = os.environ.get("OPENROUTER_API_KEY")
assert API_KEY, "Falta OPENROUTER_API_KEY. Copia .env.example a .env y pon tu key ahí."
print("API key cargada correctamente")
def preguntar(messages: list[dict], modelo: str = MODELO_FREE) -> str:
    """Envía la lista de mensajes y devuelve el texto de la respuesta."""
    r = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": modelo, "messages": messages},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def preguntar_con_la_web(messages: list[dict], modelo: str = MODELO_FREE) -> str:
    """Envía la lista de mensajes y devuelve el texto de la respuesta."""
    plugins = [
      {
        "id": "web",
        "max_results": 3,
      }
    ]
    r = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": modelo, "messages": messages, "plugins": plugins,},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

st.title("RIMAY")
st.title("_Hablar Quechua_ is :blue[cool] :sunglasses:")
st.title("Qallarisunchik", icon=":material/dashboard:")
input = st.text_input("Español", "ingrese texto")
if st.button("Traducir"):
    with st.spinner("Traduciendo...", show_time=True):
        messages = [
            {"role": "system", "content": "Eres un traductor de quechua de Bolivia q responde de forma breve"},
            {"role": "user", "content": input},
        ]

        respuesta = preguntar_con_la_web(messages)
        print("bot>", respuesta)
    st.write(respuesta)


