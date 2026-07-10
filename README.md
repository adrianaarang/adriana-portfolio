# Adriana Portfolio — Runner + Contacto

Mi portfolio interactivo: un mini videojuego a pantalla completa (HTML5 Canvas + JS puro) en el que
recorro mi propia trayectoria, con un formulario de contacto real conectado a una API que hice en
Python (FastAPI).

## Estructura
- `frontend/index.html` — el juego a pantalla completa (lo abro directamente en el navegador).
- `frontend/Adriana_Aranguez_IA_BigData.pdf` — mi CV, enlazado desde el cartel "CV" del juego.
- `backend/main.py` — mi API en FastAPI que recibe el formulario de contacto (cartel "CONTACTO").

## Cómo lo pruebo en local
1. Backend:
   ```
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
2. Frontend: abro `frontend/index.html` directamente en el navegador (doble clic).
   El formulario del cartel CONTACTO envía los mensajes a `http://localhost:8000/contact`.
3. Para ver los mensajes recibidos: abro `http://localhost:8000/contact` en el navegador.

## Cómo lo publico de verdad
- **Backend**: lo despliego en Render (plan gratuito). Al desplegar, me da una URL como
  `https://tu-api.onrender.com`.
- **Frontend**: subo `frontend/index.html` (+ el PDF) a Netlify.
- Luego, en `frontend/index.html`, busco esta línea cerca del principio del `<script>`:
  ```js
  const CONTACT_API_URL = 'http://localhost:8000/contact';
  ```
  y la cambio por la URL real de mi backend desplegado, por ejemplo:
  ```js
  const CONTACT_API_URL = 'https://adriana-portfolio-backend.onrender.com/contact';
  ```
- En `backend/main.py`, cambio también `allow_origins=["*"]` por el dominio real de mi frontend,
  para más seguridad (por ejemplo `["https://adrianaaranguez.es"]`).

## Notificaciones por email (activado, falta mi configuración en cada despliegue)
El backend ya intenta enviarme un email a **adriaranguez89@gmail.com** cada vez que alguien rellena
el formulario. Para que funcione de verdad, tengo que configurar estas variables de entorno en el
servidor donde despliegue el backend (Render — **nunca las escribo en el código ni las comparto**):

| Variable    | Valor (con Gmail)                                    |
|-------------|-------------------------------------------------------|
| `SMTP_HOST` | `smtp.gmail.com`                                       |
| `SMTP_PORT` | `587`                                                   |
| `SMTP_USER` | mi Gmail (el que envía el aviso)                       |
| `SMTP_PASS` | una "contraseña de aplicación" (no mi contraseña normal) |

Para conseguir la contraseña de aplicación en Gmail:
1. Activo la verificación en dos pasos en mi cuenta de Google (si no la tengo ya).
2. Voy a https://myaccount.google.com/apppasswords
3. Genero una contraseña para "Correo" / "Otra app" y la copio tal cual (16 caracteres, sin espacios).
4. La pongo como `SMTP_PASS` en las variables de entorno de Render — no hace falta que la recuerde,
   solo se usa ahí.

Mientras no lo configure, el formulario sigue funcionando igual (el mensaje se guarda en
`contacts.db` y, si el backend no está accesible, se abre mi correo para quien escribe como plan B) —
simplemente no me llegará el aviso automático a la bandeja de entrada hasta que active el SMTP.

Para probarlo en local antes de desplegar:
```
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=mi_correo@gmail.com
export SMTP_PASS=mi_contraseña_de_aplicacion
uvicorn main:app --reload --port 8000
```

## El chat "AdrIA"
Responde en primera persona, como si fuera yo. Intenta usar la API de Claude primero (funciona
mientras el archivo se abre dentro de Claude). Si falla —por ejemplo, una vez publicado el sitio
fuera de Claude— cae automáticamente a un asistente local por palabras clave, así nunca se queda
sin responder.
