# Adriana Portfolio — Runner + Contacto

## Estructura
- `frontend/index.html` — el juego a pantalla completa (ábrelo directamente en el navegador).
- `frontend/Adriana_Aranguez_IA_BigData.pdf` — tu CV, enlazado desde el cartel "CV" del juego.
- `backend/main.py` — API en FastAPI que recibe el formulario de contacto (cartel "CONTACTO").

## Cómo probarlo en local
1. Backend:
   ```
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
2. Frontend: abre `frontend/index.html` directamente en el navegador (doble clic).
   El formulario del cartel CONTACTO enviará los mensajes a `http://localhost:8000/contact`.
3. Para ver los mensajes recibidos: abre `http://localhost:8000/contact` en el navegador.

## Cómo publicarlo de verdad
- **Backend**: despliega la carpeta `backend/` en Render, Railway o Fly.io (todas tienen plan gratuito
  para APIs pequeñas). Al desplegar, te darán una URL como `https://tu-api.onrender.com`.
- **Frontend**: sube `frontend/index.html` (+ el PDF) a Netlify, GitHub Pages o donde prefieras.
- Luego, en `frontend/index.html`, busca esta línea cerca del principio del `<script>`:
  ```js
  const CONTACT_API_URL = 'http://localhost:8000/contact';
  ```
  y cámbiala por la URL real de tu backend desplegado, por ejemplo:
  ```js
  const CONTACT_API_URL = 'https://tu-api.onrender.com/contact';
  ```
- En `backend/main.py`, cambia también `allow_origins=["*"]` por el dominio real de tu frontend,
  para más seguridad (por ejemplo `["https://adriana-portfolio.netlify.app"]`).

## Notificaciones por email (activado, falta tu configuración)
El backend ya intenta enviarte un email a **adriaranguez89@gmail.com** cada vez que alguien rellena
el formulario. Para que funcione de verdad, tienes que configurar estas variables de entorno en el
servidor donde despliegues el backend (Render, Railway, etc. — **nunca las escribas en el código ni
las compartas por chat**):

| Variable    | Valor (ejemplo con Gmail)                          |
|-------------|-----------------------------------------------------|
| `SMTP_HOST` | `smtp.gmail.com`                                     |
| `SMTP_PORT` | `587`                                                 |
| `SMTP_USER` | tu dirección de Gmail (la que envía el aviso)        |
| `SMTP_PASS` | una "contraseña de aplicación" (no tu contraseña normal) |

Para conseguir la contraseña de aplicación en Gmail:
1. Activa la verificación en dos pasos en tu cuenta de Google (si no la tienes ya).
2. Ve a https://myaccount.google.com/apppasswords
3. Genera una contraseña para "Correo" / "Otra app" y cópiala tal cual (16 caracteres, sin espacios).
4. Ponla como `SMTP_PASS` en las variables de entorno del hosting — no hace falta que la recuerdes,
   solo se usa ahí.

Mientras no configures esto, el formulario sigue funcionando igual (el mensaje se guarda en
`contacts.db` y, si el backend no está accesible, se abre el correo de quien escribe como plan B) —
simplemente no te llegará el aviso automático a la bandeja de entrada hasta que actives el SMTP.

Para probarlo en local antes de desplegar:
```
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=tu_correo@gmail.com
export SMTP_PASS=tu_contraseña_de_aplicacion
uvicorn main:app --reload --port 8000
```

## El chat "AdrIA"
Intenta usar la API de Claude primero (funciona mientras el archivo se abra dentro de Claude).
Si falla —por ejemplo, una vez publicado el sitio fuera de Claude— cae automáticamente a un
asistente local por palabras clave, así nunca se queda sin responder.
