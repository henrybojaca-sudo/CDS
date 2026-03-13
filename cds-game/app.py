import streamlit as st
import pandas as pd
import requests
import random
from io import BytesIO
from PIL import Image

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Riesgo País — CDS Challenge",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────
# MAPA NOMBRE (español) → CÓDIGO ISO2  para flagcdn.com
# ─────────────────────────────────────────────────────────────────
COUNTRY_ISO = {
    "Estados Unidos": "us",
    "Brasil":         "br",
    "Colombia":       "co",
    "Chile":          "cl",
    "México":         "mx",
    "Panamá":         "pa",
    "Perú":           "pe",
    "Argentina":      "ar",
    "Ecuador":        "ec",
    "Costa Rica":     "cr",
    "Canadá":         "ca",
    "El Salvador":    "sv",
    "Guatemala":      "gt",
    "Uruguay":        "uy",
    "Nicaragua":      "ni",
    "Reino Unido":    "gb",
    "Francia":        "fr",
    "Alemania":       "de",
    "Italia":         "it",
    "España":         "es",
    "Portugal":       "pt",
    "Suecia":         "se",
    "Países Bajos":   "nl",
    "Suiza":          "ch",
    "Grecia":         "gr",
    "Austria":        "at",
    "Bélgica":        "be",
    "Bulgaria":       "bg",
    "Croacia":        "hr",
    "Dinamarca":      "dk",
    "Egipto":         "eg",
    "Finlandia":      "fi",
    "Hungría":        "hu",
    "Israel":         "il",
    "Kazajistán":     "kz",
    "Polonia":        "pl",
    "Qatar":          "qa",
    "Rumanía":        "ro",
    "Eslovaquia":     "sk",
    "Sudáfrica":      "za",
    "Checa":          "cz",
    "Eslovenia":      "si",
    "Letonia":        "lv",
    "Lituania":       "lt",
    "Estonia":        "ee",
    "Serbia":         "rs",
    "Bahrein":        "bh",
    "Nigeria":        "ng",
    "Argelia":        "dz",
    "Irak":           "iq",
    "Chipre":         "cy",
    "Dubai":          "ae",
    "Irlanda":        "ie",
    "Noruega":        "no",
    "Arabia Saudita": "sa",
    "Kuwait":         "kw",
    "Omán":           "om",
    "Tunisia":        "tn",
    "Turquía":        "tr",
    "Islanda":        "is",
    "Abu Dhabi":      "ae",
    "Marruecos":      "ma",
    "Ghana":          "gh",
    "Gabón":          "ga",
    "Kenia":          "ke",
    "Angola":         "ao",
    "Camerún":        "cm",
    "Ruanda":         "rw",
    "Senegal":        "sn",
    "Zambia":         "zm",
    "Etiopía":        "et",
    "Namibia":        "na",
    "Japón":          "jp",
    "Australia":      "au",
    "N. Zelanda":     "nz",
    "Sur Corea":      "kr",
    "China":          "cn",
    "Hong Kong":      "hk",
    "India":          "in",
    "Indonesia":      "id",
    "Malasia":        "my",
    "Filipinas":      "ph",
    "Pakistán":       "pk",
    "Tailandia":      "th",
    "Vietnam":        "vn",
    "Mongolia":       "mn",
}

# ─────────────────────────────────────────────────────────────────
# DATOS EMBEBIDOS (Global_CDS.xlsx — columna A: país, col H: 1W Avg)
# ─────────────────────────────────────────────────────────────────
DEFAULT_DATA = [
    ("Estados Unidos", 38.73), ("Brasil", 133.76), ("Colombia", 228.29),
    ("Chile", 51.69), ("México", 91.32), ("Panamá", 116.45),
    ("Perú", 74.00), ("Argentina", 565.16), ("Ecuador", 432.57),
    ("Costa Rica", 155.35), ("Canadá", 19.54), ("El Salvador", 283.89),
    ("Guatemala", 157.60), ("Uruguay", 61.38), ("Nicaragua", 479.35),
    ("Reino Unido", 17.96), ("Francia", 28.24), ("Alemania", 9.10),
    ("Italia", 28.72), ("España", 18.63), ("Portugal", 17.78),
    ("Suecia", 8.27), ("Países Bajos", 7.78), ("Suiza", 13.55),
    ("Grecia", 29.37), ("Austria", 14.70), ("Bélgica", 17.05),
    ("Bulgaria", 53.62), ("Croacia", 61.07), ("Dinamarca", 8.75),
    ("Egipto", 345.72), ("Finlandia", 13.63), ("Hungría", 103.29),
    ("Israel", 87.49), ("Kazajistán", 94.19), ("Polonia", 63.62),
    ("Qatar", 41.92), ("Rumanía", 136.76), ("Eslovaquia", 40.39),
    ("Sudáfrica", 152.82), ("Checa", 30.31), ("Eslovenia", 35.43),
    ("Letonia", 56.71), ("Lituania", 59.50), ("Estonia", 67.60),
    ("Serbia", 146.45), ("Bahrein", 255.17), ("Nigeria", 327.19),
    ("Argelia", 91.67), ("Irak", 298.02), ("Chipre", 48.62),
    ("Dubai", 66.18), ("Irlanda", 16.49), ("Noruega", 9.07),
    ("Arabia Saudita", 84.83), ("Kuwait", 62.19), ("Omán", 90.34),
    ("Tunisia", 715.47), ("Turquía", 252.87), ("Islanda", 36.78),
    ("Abu Dhabi", 43.14), ("Marruecos", 86.40), ("Ghana", 361.73),
    ("Gabón", 760.72), ("Kenia", 401.32), ("Angola", 572.79),
    ("Camerún", 640.01), ("Ruanda", 378.01), ("Senegal", 1084.97),
    ("Zambia", 368.87), ("Etiopía", 3432.69), ("Namibia", 297.74),
    ("Japón", 26.87), ("Australia", 14.67), ("N. Zelanda", 14.69),
    ("Sur Corea", 27.18), ("China", 46.74), ("Hong Kong", 28.64),
    ("India", 58.63), ("Indonesia", 88.89), ("Malasia", 44.57),
    ("Filipinas", 68.13), ("Pakistán", 519.72), ("Tailandia", 46.82),
    ("Vietnam", 87.35), ("Mongolia", 232.40),
]

# Separadores regionales del Excel (no son países)
NON_COUNTRIES = {"América", "EMEA", "Asia/Pacífico", "Name"}

# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_flag(country_name: str):
    """Descarga bandera desde flagcdn.com. Retorna imagen PIL o None."""
    iso = COUNTRY_ISO.get(country_name)
    if not iso:
        for k, v in COUNTRY_ISO.items():
            if k.lower() == country_name.lower():
                iso = v
                break
    if not iso:
        return None
    url = f"https://flagcdn.com/w320/{iso}.png"
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content))
    except Exception:
        pass
    return None


def load_excel(uploaded_file) -> pd.DataFrame | None:
    """Lee archivo Excel del usuario: col A = país, col H = CDS."""
    try:
        raw = pd.read_excel(uploaded_file, header=None)
        rows = []
        for _, row in raw.iterrows():
            name = str(row[0]).strip()
            if name in NON_COUNTRIES or name == "nan":
                continue
            cds = row[7] if len(row) > 7 else None
            try:
                cds_val = float(cds)
                rows.append((name, round(cds_val, 2)))
            except (TypeError, ValueError):
                continue
        if len(rows) < 2:
            st.error("El archivo debe tener al menos 2 países con CDS válido en la columna H.")
            return None
        return pd.DataFrame(rows, columns=["Pais", "CDS"]).reset_index(drop=True)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None


def default_df() -> pd.DataFrame:
    return pd.DataFrame(DEFAULT_DATA, columns=["Pais", "CDS"])


def pick_pair(df: pd.DataFrame, used: set):
    """Elige par aleatorio (i,j) i<j no usado aún."""
    idx = list(df.index)
    candidates = [(i, j) for i in idx for j in idx if i < j and (i, j) not in used]
    return random.choice(candidates) if candidates else None


# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "df":               default_df(),
        "score":            0,
        "best":             0,
        "game_over":        False,
        "game_started":     False,
        "current_pair":     None,
        "used_pairs":       set(),
        "feedback":         None,   # "correct" | "wrong" | "completed"
        "correct_country":  None,
        "round_active":     True,
        "show_data":        False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_game():
    st.session_state.score         = 0
    st.session_state.game_over     = False
    st.session_state.game_started  = True
    st.session_state.current_pair  = None
    st.session_state.used_pairs    = set()
    st.session_state.feedback      = None
    st.session_state.correct_country = None
    st.session_state.round_active  = True

def advance():
    """Prepara la siguiente ronda."""
    st.session_state.feedback         = None
    st.session_state.correct_country  = None
    st.session_state.round_active     = True
    pair = pick_pair(st.session_state.df, st.session_state.used_pairs)
    if pair is None:
        st.session_state.game_over = True
        st.session_state.feedback  = "completed"
    else:
        st.session_state.current_pair = pair
        st.session_state.used_pairs.add(pair)


# ─────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Cabecera ── */
    .header-box {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b3a5c 60%, #0d1b2a 100%);
        border-radius: 20px;
        padding: 32px 24px 24px;
        text-align: center;
        margin-bottom: 28px;
        border: 1px solid #2a5298;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    }
    .header-box h1 {
        color: #f0c040;
        font-size: 2.1rem;
        font-weight: 900;
        margin: 0 0 6px;
        letter-spacing: -0.5px;
    }
    .header-box p {
        color: #a8c4e0;
        font-size: 1rem;
        margin: 0;
    }

    /* ── Score bar ── */
    .score-bar {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-bottom: 22px;
    }
    .score-chip {
        background: #1b3a5c;
        border: 1.5px solid #2a5298;
        border-radius: 50px;
        padding: 8px 22px;
        color: #f0c040;
        font-size: 1rem;
        font-weight: 700;
    }
    .best-chip {
        background: #1b2a1b;
        border: 1.5px solid #2a7a2a;
        border-radius: 50px;
        padding: 8px 22px;
        color: #6fcf97;
        font-size: 1rem;
        font-weight: 700;
    }

    /* ── Tarjeta de país ── */
    .country-card {
        background: #f8faff;
        border: 2px solid #dbe4f0;
        border-radius: 20px;
        padding: 22px 14px 18px;
        text-align: center;
        transition: box-shadow .2s;
        min-height: 220px;
    }
    .country-card:hover { box-shadow: 0 6px 24px rgba(42,82,152,0.18); }
    .country-name {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0d1b2a;
        margin-top: 14px;
    }
    .vs-label {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 900;
        color: #b0bec5;
        padding-top: 70px;
    }

    /* ── Instrucción ── */
    .instruction {
        background: #e8f1fb;
        border-left: 5px solid #1b3a5c;
        border-radius: 10px;
        padding: 14px 18px;
        color: #0d1b2a;
        font-size: .97rem;
        margin-bottom: 20px;
        font-weight: 600;
    }

    /* ── Feedback ── */
    .fb-correct {
        background: #d4f1e0;
        border: 2px solid #27ae60;
        border-radius: 14px;
        padding: 16px 20px;
        color: #145a32;
        font-size: 1.05rem;
        font-weight: 700;
        text-align: center;
        margin: 18px 0 10px;
    }
    .fb-wrong {
        background: #fde8e8;
        border: 2px solid #e74c3c;
        border-radius: 14px;
        padding: 16px 20px;
        color: #7b241c;
        font-size: 1.05rem;
        font-weight: 700;
        text-align: center;
        margin: 18px 0 10px;
    }
    .fb-complete {
        background: #fef9e7;
        border: 2px solid #f0c040;
        border-radius: 14px;
        padding: 16px 20px;
        color: #7d6608;
        font-size: 1.05rem;
        font-weight: 700;
        text-align: center;
        margin: 18px 0 10px;
    }

    /* ── Botones de elección ── */
    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: .97rem !important;
        padding: 12px 10px !important;
        width: 100% !important;
        transition: transform .1s, box-shadow .1s !important;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.18) !important;
    }

    /* ── Bandera sin dato ── */
    .flag-placeholder {
        width: 100%;
        height: 110px;
        background: #e9ecef;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    init_state()
    inject_css()

    # ── Cabecera ─────────────────────────────────────────────────
    st.markdown("""
    <div class="header-box">
      <h1>🌍 ¿Quién tiene Mayor Riesgo País?</h1>
      <p>Selecciona el país con el CDS (Credit Default Swap) más alto &nbsp;·&nbsp; Posgrado en Finanzas</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Score bar ─────────────────────────────────────────────────
    score = st.session_state.score
    best  = st.session_state.best
    st.markdown(f"""
    <div class="score-bar">
      <div class="score-chip">🔥 Racha actual: {score}</div>
      <div class="best-chip">🏆 Mejor racha: {best}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar: carga de archivo ────────────────────────────────
    with st.sidebar:
        st.markdown("### 📂 Datos")
        st.markdown(
            "El juego usa los datos de **Global CDS** precargados. "
            "Puedes reemplazarlos con tu propio archivo:"
        )
        uploaded = st.file_uploader(
            "Subir Excel (col A = País, col H = CDS)",
            type=["xlsx"],
            label_visibility="visible",
        )
        if uploaded:
            df_new = load_excel(uploaded)
            if df_new is not None:
                st.session_state.df = df_new
                reset_game()
                advance()
                st.success(f"✅ {len(df_new)} países cargados.")
                st.rerun()

        st.markdown("---")
        if st.checkbox("📊 Ver tabla de CDS", value=st.session_state.show_data, key="show_data"):
            df_show = st.session_state.df.copy()
            df_show.columns = ["País", "CDS (pb)"]
            df_show = df_show.sort_values("CDS (pb)", ascending=False).reset_index(drop=True)
            st.dataframe(df_show, hide_index=True, use_container_width=True, height=500)

        st.markdown("---")
        st.markdown(
            "<small>**CDS** = Credit Default Swap. Mide el costo de asegurar deuda soberana. "
            "A mayor CDS, mayor riesgo percibido por el mercado.</small>",
            unsafe_allow_html=True,
        )

    # ── Botón inicio / nuevo juego ────────────────────────────────
    col_start, col_empty = st.columns([1, 2])
    with col_start:
        label = "🎮 Nuevo Juego" if st.session_state.game_started else "▶️ Iniciar Juego"
        if st.button(label, type="primary", use_container_width=True):
            reset_game()
            advance()
            st.rerun()

    # ── PANTALLA DE JUEGO ─────────────────────────────────────────
    if st.session_state.game_started and not st.session_state.game_over:
        pair = st.session_state.current_pair
        if pair is None:
            st.info("Presiona **Iniciar Juego** para comenzar.")
            return

        df   = st.session_state.df
        ia, ib = pair
        ca   = df.loc[ia, "Pais"]
        cb   = df.loc[ib, "Pais"]
        cds_a = df.loc[ia, "CDS"]
        cds_b = df.loc[ib, "CDS"]
        correct = ca if cds_a > cds_b else cb

        st.markdown("---")
        st.markdown(
            '<div class="instruction">❓ <b>¿Cuál de estos dos países tiene MAYOR riesgo crediticio?</b>'
            '<br>Haz clic en el nombre del país con el CDS más alto.</div>',
            unsafe_allow_html=True,
        )

        # ── Banderas ─────────────────────────────────────────────
        col_a, col_vs, col_b = st.columns([5, 1, 5])
        with col_a:
            st.markdown('<div class="country-card">', unsafe_allow_html=True)
            flag_a = get_flag(ca)
            if flag_a:
                st.image(flag_a, use_container_width=True)
            else:
                st.markdown('<div class="flag-placeholder">🏳️</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="country-name">{ca}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_vs:
            st.markdown('<div class="vs-label">VS</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="country-card">', unsafe_allow_html=True)
            flag_b = get_flag(cb)
            if flag_b:
                st.image(flag_b, use_container_width=True)
            else:
                st.markdown('<div class="flag-placeholder">🏳️</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="country-name">{cb}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")

        # ── Botones de respuesta ──────────────────────────────────
        if st.session_state.round_active:
            btn_a_col, _, btn_b_col = st.columns([5, 1, 5])

            with btn_a_col:
                if st.button(f"🗳️ {ca}", key="btn_a", use_container_width=True):
                    if ca == correct:
                        st.session_state.score += 1
                        st.session_state.best = max(st.session_state.best, st.session_state.score)
                        st.session_state.feedback = "correct"
                    else:
                        st.session_state.feedback = "wrong"
                        st.session_state.game_over = True
                    st.session_state.correct_country = correct
                    st.session_state.round_active = False
                    st.rerun()

            with btn_b_col:
                if st.button(f"🗳️ {cb}", key="btn_b", use_container_width=True):
                    if cb == correct:
                        st.session_state.score += 1
                        st.session_state.best = max(st.session_state.best, st.session_state.score)
                        st.session_state.feedback = "correct"
                    else:
                        st.session_state.feedback = "wrong"
                        st.session_state.game_over = True
                    st.session_state.correct_country = correct
                    st.session_state.round_active = False
                    st.rerun()

        # ── Feedback ronda correcta ───────────────────────────────
        if st.session_state.feedback == "correct":
            c_name = st.session_state.correct_country
            c_cds  = df.loc[df["Pais"] == c_name, "CDS"].values[0]
            other  = cb if c_name == ca else ca
            o_cds  = df.loc[df["Pais"] == other, "CDS"].values[0]
            st.markdown(f"""
            <div class="fb-correct">
            ✅ ¡Correcto! &nbsp;<b>{c_name}</b> tiene mayor riesgo
            &nbsp;·&nbsp; CDS: <b>{c_cds:,.2f} pb</b>
            &nbsp;vs&nbsp; {other}: {o_cds:,.2f} pb
            </div>
            """, unsafe_allow_html=True)

            _, col_next, _ = st.columns([2, 3, 2])
            with col_next:
                if st.button("➡️ Siguiente ronda", type="primary", use_container_width=True):
                    advance()
                    st.rerun()

    # ── GAME OVER ─────────────────────────────────────────────────
    if st.session_state.game_over:
        fb    = st.session_state.feedback
        score = st.session_state.score
        best  = st.session_state.best
        pair  = st.session_state.current_pair
        df    = st.session_state.df

        if fb == "completed":
            st.markdown(f"""
            <div class="fb-complete">
            🎉 ¡Completaste todos los pares disponibles!<br>
            Racha final: <b>{score} aciertos consecutivos</b>
            &nbsp;·&nbsp; Mejor racha histórica: <b>{best}</b>
            </div>
            """, unsafe_allow_html=True)

        elif fb == "wrong" and pair:
            ia, ib = pair
            ca   = df.loc[ia, "Pais"]
            cb   = df.loc[ib, "Pais"]
            cds_a = df.loc[ia, "CDS"]
            cds_b = df.loc[ib, "CDS"]
            correct = st.session_state.correct_country
            c_cds   = df.loc[df["Pais"] == correct, "CDS"].values[0]
            other   = cb if correct == ca else ca
            o_cds   = df.loc[df["Pais"] == other,   "CDS"].values[0]

            st.markdown(f"""
            <div class="fb-wrong">
            ❌ ¡Incorrecto! La racha se detiene en <b>{score} acierto{"s" if score!=1 else ""}</b>.<br>
            La respuesta correcta era <b>{correct}</b>
            &nbsp;·&nbsp; CDS: <b>{c_cds:,.2f} pb</b>
            &nbsp;vs&nbsp; {other}: {o_cds:,.2f} pb
            </div>
            """, unsafe_allow_html=True)

            # Mostrar banderas del par fallido
            col_a, col_vs, col_b = st.columns([5, 1, 5])
            with col_a:
                flag_a = get_flag(ca)
                if flag_a:
                    st.image(flag_a, use_container_width=True)
                st.markdown(f"<div style='text-align:center;font-weight:800;font-size:1.1rem'>{ca}<br><span style='color:#888;font-size:.9rem'>CDS: {cds_a:,.2f} pb</span></div>", unsafe_allow_html=True)
            with col_vs:
                st.markdown('<div class="vs-label">VS</div>', unsafe_allow_html=True)
            with col_b:
                flag_b = get_flag(cb)
                if flag_b:
                    st.image(flag_b, use_container_width=True)
                st.markdown(f"<div style='text-align:center;font-weight:800;font-size:1.1rem'>{cb}<br><span style='color:#888;font-size:.9rem'>CDS: {cds_b:,.2f} pb</span></div>", unsafe_allow_html=True)

        st.markdown("")
        _, col_btn, _ = st.columns([2, 3, 2])
        with col_btn:
            if st.button("🔄 Jugar de nuevo", type="primary", use_container_width=True):
                reset_game()
                advance()
                st.rerun()

    # ── Pantalla de bienvenida ────────────────────────────────────
    elif not st.session_state.game_started:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0; color:#546e7a;">
          <div style="font-size:4rem;">🎯</div>
          <div style="font-size:1.1rem; font-weight:600; margin-top:12px;">
            Presiona <b>Iniciar Juego</b> para comenzar
          </div>
          <div style="font-size:.95rem; margin-top:8px; color:#90a4ae;">
            El juego incluye 86 países con datos reales de CDS
          </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
