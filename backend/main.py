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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator

app = FastAPI(title="Adriana Portfolio — Contact API")

# En producción, cambia "*" por el dominio real donde publiques la web
# (por ejemplo: ["https://adriana-portfolio.netlify.app"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    Envía un email de notificación a Adriana cuando llega un mensaje nuevo.
    Necesita estas variables de entorno configuradas en el servidor donde
    despliegues el backend (NUNCA las escribas en este archivo ni en el chat):
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    Opcional: NOTIFY_EMAIL (si no se configura, usa adriaranguez89@gmail.com).

    Con Gmail: SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, SMTP_USER=tu Gmail,
    SMTP_PASS= una "contraseña de aplicación" (no tu contraseña normal — se
    genera en https://myaccount.google.com/apppasswords, requiere tener
    la verificación en dos pasos activada).
    """
    import smtplib
    from email.message import EmailMessage

    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    to_email = os.environ.get("NOTIFY_EMAIL", "adriaranguez89@gmail.com")

    if not all([host, user, password]):
        print("[aviso] Envío de email no configurado (faltan SMTP_HOST/SMTP_USER/SMTP_PASS). "
              "El mensaje ya quedó guardado en contacts.db de todas formas.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"Nuevo mensaje de {form.name} (portfolio)"
    msg["From"] = user
    msg["To"] = to_email
    msg["Reply-To"] = form.email
    msg.set_content(f"De: {form.name} <{form.email}>\n\n{form.message}")

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
