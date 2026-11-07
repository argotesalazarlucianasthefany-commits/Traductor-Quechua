import html
import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://openrouter.ai/api/v1"
MODELO_FREE = "nvidia/nemotron-3-ultra-550b-a55b:free"

API_KEY = os.environ.get("OPENROUTER_API_KEY")
assert API_KEY, "Falta OPENROUTER_API_KEY. Copia .env.example a .env y pon tu key ahí."

st.set_page_config(
    page_title="RIMAY · Traductor Quechua",
    page_icon="🪶",
    layout="centered",
)


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
        json={"model": modelo, "messages": messages, "plugins": plugins},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


st.markdown(
    """
    <style>
    :root {
      --rimay-bg: #f4eee2;
      --rimay-surface: #fffaf1;
      --rimay-surface-2: #ece3d4;
      --rimay-input: #fffdf8;
      --rimay-text: #24313a;
      --rimay-muted: #6c7a83;
      --rimay-border: #ded4c2;
      --rimay-border-strong: #cabca5;
      --rimay-accent: #52738b;
      --rimay-accent-hover: #405d73;
      --rimay-accent-soft: #e2ebf1;
      --rimay-on-accent: #fdfbf6;
      --rimay-ornament: #c2ab86;
      --rimay-danger: #a4432f;
      --rimay-danger-bg: #fdf1ed;
      --rimay-danger-border: #ecc9bd;
    }

    .stApp {
      background-color: var(--rimay-bg);
      background-image:
        radial-gradient(1200px 620px at 10% -10%, rgba(82, 115, 139, 0.16), transparent 62%),
        radial-gradient(900px 520px at 100% 0%, rgba(194, 171, 134, 0.22), transparent 58%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='72' height='72' viewBox='0 0 72 72'%3E%3Cpath d='M36 6 66 36 36 66 6 36Z' fill='none' stroke='%2352738b' stroke-opacity='.07'/%3E%3Cpath d='M36 20 52 36 36 52 20 36Z' fill='none' stroke='%2352738b' stroke-opacity='.05'/%3E%3C/svg%3E");
      background-attachment: fixed;
    }

    [data-testid="stHeader"] {
      background: transparent;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
      max-width: 720px;
      padding-top: 2.8rem;
      padding-bottom: 2.5rem;
    }

    /* Hero */
    .rimay-hero {
      margin: 0 0 1.8rem;
      text-align: center;
    }

    .rimay-kicker {
      display: inline-block;
      padding: 0.32rem 0.85rem;
      color: var(--rimay-accent);
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.28em;
      text-transform: uppercase;
      background: var(--rimay-surface);
      border: 1px solid var(--rimay-border);
      border-radius: 999px;
    }

    .rimay-hero h1 {
      margin: 0.7rem 0 0.25rem;
      color: var(--rimay-text);
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(2.1rem, 5vw, 2.8rem);
      font-weight: 600;
      letter-spacing: -0.02em;
      line-height: 1.15;
    }

    .rimay-hero p {
      margin: 0;
      color: var(--rimay-muted);
      font-size: 0.96rem;
    }

    .rimay-band {
      width: min(320px, 70%);
      height: 14px;
      margin: 1.2rem auto 0;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='36' height='14' viewBox='0 0 36 14'%3E%3Cpath d='M18 1 25 7 18 13 11 7Z' fill='none' stroke='%2352738b' stroke-width='1.1'/%3E%3Cpath d='M3 7 6 4 9 7 6 10Z' fill='%23c2ab86'/%3E%3Cpath d='M33 7 30 4 27 7 30 10Z' fill='%23c2ab86'/%3E%3C/svg%3E") repeat-x center / auto 14px;
      opacity: 0.8;
    }

    /* Tarjeta del formulario */
    .st-key-rimay-card {
      position: relative;
      overflow: hidden;
      background: var(--rimay-surface);
      border: 1px solid var(--rimay-border) !important;
      border-radius: 16px !important;
      box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.65) inset,
        0 14px 30px -24px rgba(36, 49, 58, 0.55);
    }

    .st-key-rimay-card::before {
      content: "";
      position: absolute;
      inset: 0 0 auto 0;
      height: 3px;
      background: linear-gradient(90deg, var(--rimay-accent), var(--rimay-ornament), var(--rimay-accent));
      opacity: 0.55;
    }

    /* Texto general dentro de la app */
    .stApp,
    .stMarkdown p,
    [data-testid="stWidgetLabel"] p {
      color: var(--rimay-text);
    }

    [data-testid="stWidgetLabel"] p {
      font-size: 0.92rem;
      font-weight: 600;
    }

    /* Campo de texto */
    .stTextInput input {
      padding: 0.7rem 0.85rem !important;
      color: var(--rimay-text) !important;
      background: var(--rimay-input) !important;
      border: 1px solid var(--rimay-border) !important;
      border-radius: 10px !important;
      box-shadow: inset 0 1px 2px rgba(36, 49, 58, 0.05);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .stTextInput input::placeholder {
      color: var(--rimay-muted) !important;
    }

    .stTextInput input:focus {
      border-color: var(--rimay-accent) !important;
      box-shadow:
        inset 0 1px 2px rgba(36, 49, 58, 0.05),
        0 0 0 3px rgba(82, 115, 139, 0.22) !important;
    }

    .stTextInput [data-baseweb="input"] {
      background: transparent !important;
      border: 0 !important;
    }

    /* Botón principal */
    .stButton > button {
      width: 100%;
      padding: 0.7rem 1.1rem;
      color: var(--rimay-on-accent) !important;
      font-size: 0.98rem;
      font-weight: 600;
      background: linear-gradient(180deg, var(--rimay-accent), var(--rimay-accent-hover));
      border: 0;
      border-radius: 10px;
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.18),
        0 8px 18px -10px rgba(64, 93, 115, 0.85);
      transition: transform 0.1s ease, box-shadow 0.15s ease, background 0.15s ease;
    }

    .stButton > button * {
      color: inherit !important;
    }

    .stButton > button:hover {
      color: var(--rimay-on-accent) !important;
      background: linear-gradient(180deg, var(--rimay-accent-hover), var(--rimay-accent-hover));
      border: 0;
      transform: translateY(-1px);
    }

    .stButton > button:active {
      transform: translateY(0);
    }

    .stButton > button:focus:not(:active) {
      border: 0;
      box-shadow:
        0 0 0 3px rgba(82, 115, 139, 0.22),
        0 8px 18px -10px rgba(64, 93, 115, 0.85) !important;
    }

    /* Spinner */
    .stSpinner > div {
      border-top-color: var(--rimay-accent) !important;
    }

    [data-testid="stSpinner"] p {
      color: var(--rimay-accent);
      font-weight: 600;
    }

    /* Resultado */
    .rimay-result {
      position: relative;
      margin-top: 1.1rem;
      padding: 1.15rem 1.25rem;
      overflow: hidden;
      background: linear-gradient(180deg, var(--rimay-accent-soft) 0%, var(--rimay-surface) 80%);
      border: 1px solid var(--rimay-border);
      border-radius: 16px;
      box-shadow:
        0 1px 0 rgba(255, 255, 255, 0.65) inset,
        0 14px 30px -24px rgba(36, 49, 58, 0.55);
    }

    .rimay-result::before {
      content: "";
      position: absolute;
      inset: 0 0 auto 0;
      height: 3px;
      background: linear-gradient(90deg, var(--rimay-accent), var(--rimay-ornament), var(--rimay-accent));
      opacity: 0.55;
    }

    .rimay-label {
      color: var(--rimay-accent);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    .rimay-output {
      margin: 0.5rem 0 0;
      color: var(--rimay-text);
      font-size: 1.16rem;
      line-height: 1.6;
      white-space: pre-wrap;
    }

    /* Error */
    .rimay-error {
      margin-top: 1.1rem;
      padding: 0.85rem 1rem;
      color: var(--rimay-danger);
      font-size: 0.92rem;
      background: var(--rimay-danger-bg);
      border: 1px solid var(--rimay-danger-border);
      border-radius: 12px;
    }

    /* Pie */
    .rimay-foot {
      margin: 2rem 0 0;
      color: var(--rimay-muted);
      font-size: 0.8rem;
      text-align: center;
    }

    .rimay-foot::before {
      content: "";
      display: block;
      width: min(180px, 60%);
      height: 12px;
      margin: 0 auto 0.8rem;
      background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='36' height='14' viewBox='0 0 36 14'%3E%3Cpath d='M18 1 25 7 18 13 11 7Z' fill='none' stroke='%2352738b' stroke-width='1.1'/%3E%3Cpath d='M3 7 6 4 9 7 6 10Z' fill='%23c2ab86'/%3E%3Cpath d='M33 7 30 4 27 7 30 10Z' fill='%23c2ab86'/%3E%3C/svg%3E") repeat-x center / auto 12px;
      opacity: 0.55;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="rimay-hero">
      <span class="rimay-kicker">RIMAY</span>
      <h1>Hablar Quechua</h1>
      <p>Traductor español → quechua boliviano · OpenRouter</p>
      <div class="rimay-band"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True, key="rimay-card"):
    texto = st.text_input(
        "Español",
        placeholder="Escribe una frase en español…",
    )
    traducir = st.button("Traducir", width="stretch")


def mostrar_error(mensaje: str) -> None:
    st.markdown(
        f'<div class="rimay-error">{html.escape(mensaje)}</div>',
        unsafe_allow_html=True,
    )


if traducir:
    if not texto.strip():
        mostrar_error("Escribe algo para traducir.")
    else:
        with st.spinner("Traduciendo…"):
            messages = [
                {
                    "role": "system",
                    "content": "Eres un traductor de quechua de Bolivia q responde de forma breve",
                },
                {"role": "user", "content": texto},
            ]

            try:
                respuesta = preguntar_con_la_web(messages)
            except httpx.HTTPStatusError as error:
                codigo = error.response.status_code if error.response is not None else 0
                if codigo == 401:
                    mensaje = "API key inválida o revocada. Revísala en openrouter.ai/keys."
                elif codigo == 402:
                    mensaje = "La cuenta no tiene créditos. Usa un modelo gratuito o agrega saldo."
                elif codigo == 404:
                    mensaje = "No se encontró el modelo. Revisa su ID en openrouter.ai/models."
                elif codigo == 429:
                    mensaje = "Límite de solicitudes alcanzado (429). Espera un poco y vuelve a intentar."
                elif codigo >= 500:
                    mensaje = f"OpenRouter tuvo un error ({codigo}). Intenta de nuevo en unos segundos."
                else:
                    mensaje = f"Error {codigo}: {error.response.text if error.response is not None else error}"
                mostrar_error(mensaje)
            except httpx.RequestError:
                mostrar_error("No se pudo conectar con OpenRouter. Revisa tu conexión.")
            else:
                st.markdown(
                    f"""
                    <div class="rimay-result">
                      <span class="rimay-label">Traducción</span>
                      <p class="rimay-output">{html.escape(respuesta)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

st.markdown(
    '<p class="rimay-foot">Las traducciones las genera un modelo de IA y pueden contener errores.</p>',
    unsafe_allow_html=True,
)
