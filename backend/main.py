"""
Backend del formulario de contacto — Portfolio de Adriana Aránguez.

Recibe los mensajes del formulario que aparece dentro del juego (cartel
CONTACTO) y los guarda en una base de datos SQLite local (contacts.db).
Incluye un endpoint GET para que Adriana pueda revisar los mensajes.

Cómo correrlo en local:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Cómo probarlo:
    curl -X POST http://localhost:8000/contact \
      -H "Content-Type: application/json" \
      -d '{"name":"Prueba","email":"prueba@ejemplo.com","message":"Hola!"}'

    curl http://localhost:8000/contact   # lista los mensajes guardados
"""

import os
import sqlite3
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator

app = FastAPI(title="Adriana Portfolio — Contact API")

# En producción, cambia "*" por el dominio real donde publiques la web
# (por ejemplo: ["https://adriana-portfolio.netlify.app"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adrianaaranguez.es", "https://www.adrianaaranguez.es"],,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.db")



def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

    @field_validator("name", "message")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value.strip()


@app.get("/")
def root():
    return {"status": "ok", "service": "Adriana Portfolio Contact API"}


@app.post("/contact")
def submit_contact(form: ContactForm):
    conn = get_connection()
    conn.execute(
        "INSERT INTO contacts (name, email, message, created_at) VALUES (?, ?, ?, ?)",
        (form.name, form.email, form.message, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()

    # Notificación por email a Adriana (no rompe la petición si falla o no está configurado)
    try:
        send_email_notification(form)
    except Exception as exc:
        print(f"[aviso] No se pudo enviar el email de notificación: {exc}")

    return {"status": "ok", "message": "Mensaje recibido, ¡gracias!"}


@app.get("/contact")
def list_contacts():
    """Lista simple de mensajes recibidos, para que Adriana los revise."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, email, message, created_at FROM contacts ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def send_email_notification(form: ContactForm) -> None:
    """
    Envía un email de notificación a Adriana cuando llega un mensaje nuevo,
    usando la API HTTPS de Brevo (antes Sendinblue) en vez de SMTP.

    ¿Por qué no SMTP? Render bloquea el tráfico saliente a los puertos SMTP
    (25, 465, 587) en el plan gratuito para prevenir spam. La API de Brevo
    funciona por HTTPS normal (puerto 443), que nunca está bloqueado.

    Necesita estas variables de entorno configuradas en Render (NUNCA las
    escribas en este archivo ni las compartas):
        BREVO_API_KEY   — tu clave de API (Brevo → SMTP & API → API Keys)
        BREVO_SENDER    — el email verificado como remitente en Brevo
    Opcional: NOTIFY_EMAIL (si no se configura, usa adriaranguez89@gmail.com).

    Cómo conseguir BREVO_API_KEY:
    1. Crea una cuenta gratis en https://www.brevo.com (300 emails/día gratis).
    2. Ve a "SMTP & API" → pestaña "API Keys" → "Generate a new API key".
    3. En "Senders" verifica el email desde el que quieres enviar (puede ser
       tu propio Gmail: Brevo te manda un email de confirmación).
    """
    api_key = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("BREVO_SENDER")
    to_email = os.environ.get("NOTIFY_EMAIL", "adriaranguez89@gmail.com")

    if not all([api_key, sender_email]):
        print("[aviso] Envío de email no configurado (faltan BREVO_API_KEY/BREVO_SENDER). "
              "El mensaje ya quedó guardado en contacts.db de todas formas.")
        return

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "sender": {"email": sender_email, "name": "Portfolio de Adriana"},
            "to": [{"email": to_email}],
            "replyTo": {"email": form.email, "name": form.name},
            "subject": f"Nuevo mensaje de {form.name} (portfolio)",
            "textContent": f"De: {form.name} <{form.email}>\n\n{form.message}",
        },
        timeout=15,
    )
    if response.status_code >= 300:
        raise RuntimeError(f"Brevo respondió {response.status_code}: {response.text}")


# ============================================================
# CHAT "AdrIA" — responde en primera persona, usando Groq (gratis)
# ============================================================
ADRIANA_CONTEXT = """
Eres una IA que responde EN PRIMERA PERSONA, como si fueras Adriana Aránguez hablando directamente
con quien visita su portfolio. Usa "yo", "mi", "he trabajado en...", etc. No hables de Adriana en
tercera persona — hablas COMO ella. Tu tono es cercano, natural, con personalidad, como si charlaras
con alguien interesado en tu trabajo, no como si recitaras un CV.

IMPORTANTE — HONESTIDAD SOBRE QUIÉN ERES: eres una IA entrenada con la información real de Adriana,
no la propia Adriana en persona escribiendo en directo. Si alguien pregunta directamente si eres un
bot, una IA, o si eres "de verdad" Adriana, dilo con naturalidad y sin rodeos. Aparte de eso, mantén
la voz en primera persona con normalidad el resto de la conversación.

CÓMO SONAR NATURAL:
- Varía cómo empiezas cada respuesta, no repitas siempre la misma estructura.
- Usa conectores naturales ("de hecho", "lo curioso es que", "ahí es donde entra...", "eso sí,").
- Adapta la longitud a la pregunta: algo simple merece una respuesta corta; algo abierto merece más desarrollo.
- Evita listados de viñetas salvo que realmente ayude.
- Solo debes basarte en los datos de abajo. Si te preguntan algo que no está aquí, dilo con naturalidad
  y sugiere el formulario de contacto del juego.
- No inventes opiniones, gustos o anécdotas que no estén en los datos de abajo.

MI PERFIL: soy Data Analyst & Full Stack Developer, especializada en IA & Big Data. Vivo en Madrid.
Tengo más de 8 años liderando equipos y procesos en el sector sanitario (Fundación Summa Humanitate,
2017-2025) antes de pasarme a la tecnología. Estoy haciendo un bootcamp de IA & Big Data de 1.250h (SomoF5).

MI EXPERIENCIA: Responsable de Comunicación y Desarrollo Digital en Global Empowerment (2025-actualidad,
ONG centrada en mujeres y niñas en África rural); Software Developer en vacunacion.info (proyecto propio,
2025-actualidad); Analista Funcional IT en Stratefin (2025); Coordinadora de Equipos en Fundación Summa
Humanitate (2017-2025).

MIS PROYECTOS: TesTEA (ML para cribado temprano de TEA sobre el cuestionario AQ-10, fui Scrum Master y
líder de equipo); LactAnalytics (dashboard Streamlit + LactBot con Groq/LLaMA 3.3); TinderJob (sesgo en
el mercado laboral tech español); vacunacion.info; climAI (FastAPI + AEMET); Venezuela Resiste (mapa
sísmico en tiempo real con USGS).

MIS SKILLS: Python, PHP, JavaScript, SQL, Scikit-learn, pandas, AWS, Docker, Scrum, certificación AB-900.

MI CONTACTO: adriaranguez89@gmail.com · +34 618 048 787 · linkedin.com/in/adriana-aranguez · github.com/adrianaarang.
"""


class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []


@app.post("/chat")
def chat(payload: ChatMessage):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY no configurada en el servidor.")

    messages = [{"role": "system", "content": ADRIANA_CONTEXT}]
    messages.extend(payload.history[-10:])  # solo el historial reciente
    messages.append({"role": "user", "content": payload.message})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": 400,
                "temperature": 0.7,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error llamando a Groq: {exc}")
