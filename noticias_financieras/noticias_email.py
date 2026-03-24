"""
Noticias Financieras Automaticas
Envia un resumen de noticias financieras todos los dias entre semana a las 7:00 AM (Bogota)
"""

import feedparser
import smtplib
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz

# ============================================================
# CONFIGURACION - Edita estos valores
# ============================================================
GMAIL_USUARIO  = "henry.bojaca@gmail.com"   # Tu correo Gmail
GMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"      # App Password de Gmail (ver instrucciones abajo)

DESTINATARIOS = [
    "henry.bojaca@gmail.com",
    # Agrega mas correos aqui:
    # "otro@ejemplo.com",
]

ZONA_BOGOTA = pytz.timezone("America/Bogota")

# Fuentes RSS financieras confiables
FUENTES_RSS = [
    {"nombre": "Reuters Business",     "url": "https://feeds.reuters.com/reuters/businessNews"},
    {"nombre": "Bloomberg Markets",    "url": "https://feeds.bloomberg.com/markets/news.rss"},
    {"nombre": "El Tiempo Economia",   "url": "https://www.eltiempo.com/rss/economia.xml"},
    {"nombre": "Portafolio",           "url": "https://www.portafolio.co/rss/portafolio.xml"},
    {"nombre": "Investing.com",        "url": "https://www.investing.com/rss/news_25.rss"},
]

NOTICIAS_POR_FUENTE = 3  # Cuantas noticias tomar de cada fuente
# ============================================================


def obtener_noticias():
    """Obtiene noticias de todas las fuentes RSS configuradas."""
    todas = []
    for fuente in FUENTES_RSS:
        try:
            feed = feedparser.parse(fuente["url"])
            for entry in feed.entries[:NOTICIAS_POR_FUENTE]:
                todas.append({
                    "fuente":  fuente["nombre"],
                    "titulo":  entry.get("title", "Sin titulo"),
                    "resumen": entry.get("summary", entry.get("description", "")),
                    "url":     entry.get("link", ""),
                    "fecha":   entry.get("published", ""),
                })
        except Exception as e:
            print(f"[AVISO] No se pudo leer {fuente['nombre']}: {e}")
    return todas


def generar_html(noticias):
    """Genera el cuerpo del correo en HTML."""
    fecha_hoy = datetime.now(ZONA_BOGOTA).strftime("%A %d de %B de %Y")

    secciones_html = ""
    fuente_actual = None

    for n in noticias:
        if n["fuente"] != fuente_actual:
            if fuente_actual is not None:
                secciones_html += "</div>"
            fuente_actual = n["fuente"]
            secciones_html += f"""
            <div style="margin-bottom:24px;">
                <h2 style="color:#1a73e8;border-bottom:2px solid #1a73e8;padding-bottom:4px;">
                    {fuente_actual}
                </h2>
            """

        resumen = n["resumen"][:250] + "..." if len(n["resumen"]) > 250 else n["resumen"]

        secciones_html += f"""
            <div style="margin-bottom:16px;padding:12px;background:#f9f9f9;border-radius:6px;">
                <a href="{n['url']}" style="font-size:15px;font-weight:bold;color:#202124;text-decoration:none;">
                    {n['titulo']}
                </a>
                <p style="font-size:13px;color:#5f6368;margin:6px 0 0;">{resumen}</p>
                <small style="color:#9aa0a6;">{n['fecha']}</small>
            </div>
        """

    if fuente_actual:
        secciones_html += "</div>"

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px;">
        <div style="background:#1a73e8;padding:20px;border-radius:8px;text-align:center;">
            <h1 style="color:white;margin:0;">📊 Noticias Financieras</h1>
            <p style="color:#e8f0fe;margin:6px 0 0;">{fecha_hoy} · 7:00 AM Bogotá</p>
        </div>
        <div style="margin-top:24px;">
            {secciones_html}
        </div>
        <hr style="margin-top:30px;border:none;border-top:1px solid #e0e0e0;">
        <p style="font-size:11px;color:#9aa0a6;text-align:center;">
            Correo generado automaticamente · Solo dias habiles · Zona horaria: America/Bogota
        </p>
    </body>
    </html>
    """
    return html


def enviar_correo():
    """Obtiene noticias y envia el correo."""
    ahora = datetime.now(ZONA_BOGOTA)

    # Solo enviar en dias de semana (0=Lunes ... 4=Viernes)
    if ahora.weekday() >= 5:
        print(f"[{ahora.strftime('%Y-%m-%d %H:%M')}] Fin de semana, no se envia correo.")
        return

    print(f"[{ahora.strftime('%Y-%m-%d %H:%M')}] Obteniendo noticias...")
    noticias = obtener_noticias()

    if not noticias:
        print("[ERROR] No se obtuvieron noticias. Correo no enviado.")
        return

    html_body = generar_html(noticias)
    asunto = f"📊 Noticias Financieras - {ahora.strftime('%d/%m/%Y')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = GMAIL_USUARIO
    msg["To"]      = ", ".join(DESTINATARIOS)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USUARIO, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USUARIO, DESTINATARIOS, msg.as_string())
        print(f"[OK] Correo enviado a: {', '.join(DESTINATARIOS)}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el correo: {e}")


def main():
    print("=" * 50)
    print("  Servicio de Noticias Financieras Activo")
    print(f"  Envio programado: Lunes-Viernes 07:00 AM (Bogota)")
    print("=" * 50)

    # Programar envio diario a las 07:00
    schedule.every().day.at("07:00").do(enviar_correo)

    # Para probar ahora mismo, descomenta la siguiente linea:
    # enviar_correo()

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
