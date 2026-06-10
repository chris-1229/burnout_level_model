import streamlit as st
import pandas as pd
import pickle

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="번아웃 위험도 예측기",
    page_icon="🔥",
    layout="centered",
)

# ── 글로벌 CSS ────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* ── 전체 배경 ── */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0F0C29 0%, #302B63 50%, #24243e 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stMain"] { background: transparent !important; }
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 680px !important;
}

/* ── 폰트 기본 ── */
html, body, * { font-family: 'Inter', sans-serif; color: #F0F0F0; }

/* ── 히어로 헤더 ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.15;
    background: linear-gradient(90deg, #FF6B6B, #FFD93D, #6BCB77);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.hero-sub {
    font-size: 0.95rem;
    color: #a0a0c0;
    margin-bottom: 2rem;
    letter-spacing: 0.01em;
}

/* ── 입력 카드 ── */
.input-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2rem 2rem 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
}
.input-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9090c0;
    margin-bottom: 0.4rem;
}

/* ── Streamlit 위젯 오버라이드 ── */
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, #FF6B6B, #FFD93D) !important;
}
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important;
    color: #F0F0F0 !important;
    font-size: 1.1rem !important;
}
[data-testid="stSlider"] label, [data-testid="stNumberInput"] label {
    color: #c0c0e0 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

/* ── 예측 버튼 ── */
[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(90deg, #FF6B6B 0%, #FFD93D 50%, #6BCB77 100%) !important;
    color: #0F0C29 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 1.5rem !important;
    margin-top: 0.5rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
    cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-2px) !important;
}

/* ── 결과 카드 ── */
.result-card {
    border-radius: 24px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin: 1.5rem 0;
    animation: fadeUp 0.5s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.result-eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 0.6rem;
}
.result-level {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 0.4rem;
}
.result-sub {
    font-size: 0.9rem;
    opacity: 0.65;
}

/* ── 확률 버블 섹션 ── */
.prob-section {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}
.prob-bubble {
    flex: 1;
    background: rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 1.2rem 0.8rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
    transition: transform 0.2s;
}
.prob-bubble:hover { transform: translateY(-3px); }
.prob-pct {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
}
.prob-label {
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-top: 0.2rem;
}
.prob-bar-wrap {
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    height: 4px;
    margin-top: 0.8rem;
    overflow: hidden;
}
.prob-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
}

/* ── 워닝 ── */
[data-testid="stAlert"] {
    background: rgba(255,107,107,0.12) !important;
    border: 1px solid rgba(255,107,107,0.3) !important;
    border-radius: 12px !important;
    color: #ffb0b0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── 히어로 헤더 ──────────────────────────────────────────────
st.markdown("""
<div class="hero-title">번아웃 위험도 예측기</div>
<div class="hero-sub">생성형 AI 사용 패턴과 심리 상태를 입력하면<br>머신러닝 모델이 번아웃 위험도를 분석합니다.</div>
""", unsafe_allow_html=True)

# ── 모델 로드 ─────────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open("model.pkl", "rb") as f:
        log_model = pickle.load(f)
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    return log_model, scaler

try:
    log_model, scaler = load_model()
    model_loaded = True
except FileNotFoundError:
    st.warning("⚠️  model.pkl 또는 scaler.pkl 을 찾을 수 없어 데모 모드로 실행됩니다.")
    model_loaded = False

burnout_mapping = {"High": 2, "Medium": 1, "Low": 0}
reverse_burnout_mapping = {v: k for k, v in burnout_mapping.items()}

# ── 입력 폼 ──────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="input-label">주간 AI 사용시간</div>', unsafe_allow_html=True)
    weekly_ai_hours = st.number_input(
        "주간 생성형 AI 사용시간 (시간)",
        min_value=0.0, max_value=168.0, value=10.0, step=0.5,
        help="ChatGPT, Claude 등 생성형 AI를 사용한 주간 총 시간",
        label_visibility="collapsed",
    )
with col2:
    st.markdown('<div class="input-label">체감 AI 의존도 (1–7)</div>', unsafe_allow_html=True)
    ai_dependency = st.slider(
        "체감 AI 의존도",
        min_value=1, max_value=7, value=4,
        help="1 = 전혀 의존 안 함 · 7 = 매우 강하게 의존",
        label_visibility="collapsed",
    )

st.markdown('<div class="input-label" style="margin-top:1rem;">시험 중 불안 수준 (1–9)</div>', unsafe_allow_html=True)
anxiety_level = st.slider(
    "시험 중 불안 수준",
    min_value=1, max_value=9, value=5,
    help="1 = 매우 낮음 · 9 = 매우 높음",
    label_visibility="collapsed",
)

st.markdown('</div>', unsafe_allow_html=True)

# ── 예측 버튼 & 결과 ─────────────────────────────────────────
LEVEL_CONFIG = {
    "Low": {
        "label": "낮음 · Low",
        "color": "#6BCB77",
        "glow": "rgba(107,203,119,0.25)",
        "border": "rgba(107,203,119,0.4)",
        "desc": "현재 번아웃 위험이 낮습니다. 균형을 잘 유지하고 있어요.",
    },
    "Medium": {
        "label": "보통 · Medium",
        "color": "#FFD93D",
        "glow": "rgba(255,217,61,0.2)",
        "border": "rgba(255,217,61,0.4)",
        "desc": "번아웃 위험이 중간 수준입니다. 휴식과 조율이 필요해요.",
    },
    "High": {
        "label": "높음 · High",
        "color": "#FF6B6B",
        "glow": "rgba(255,107,107,0.25)",
        "border": "rgba(255,107,107,0.45)",
        "desc": "번아웃 위험이 높습니다. 즉각적인 휴식과 지원이 필요합니다.",
    },
}

if st.button("번아웃 위험도 분석하기 →"):
    input_data = pd.DataFrame(
        [[weekly_ai_hours, ai_dependency, anxiety_level]],
        columns=["주간_생성형AI_사용시간", "체감_AI_의존도", "시험_중_불안_수준"],
    )

    if model_loaded:
        input_scaled = scaler.transform(input_data)
        predicted_numeric = log_model.predict(input_scaled)[0]
        proba = log_model.predict_proba(input_scaled)[0]
        predicted_label = reverse_burnout_mapping[predicted_numeric]
    else:
        score = weekly_ai_hours / 20 + ai_dependency / 7 + anxiety_level / 9
        if score > 2.0:
            predicted_label, proba = "High",   [0.10, 0.25, 0.65]
        elif score > 1.2:
            predicted_label, proba = "Medium", [0.20, 0.55, 0.25]
        else:
            predicted_label, proba = "Low",    [0.70, 0.20, 0.10]

    cfg = LEVEL_CONFIG[predicted_label]
    prob_low, prob_mid, prob_high = proba[0]*100, proba[1]*100, proba[2]*100

    # 결과 카드
    st.markdown(f"""
    <div class="result-card" style="
        background: radial-gradient(ellipse at center, {cfg['glow']} 0%, rgba(15,12,41,0.6) 70%);
        border: 1.5px solid {cfg['border']};
        box-shadow: 0 0 40px {cfg['glow']};
    ">
        <div class="result-eyebrow">🔍 예측 번아웃 위험도</div>
        <div class="result-level" style="color: {cfg['color']};">{cfg['label']}</div>
        <div class="result-sub">{cfg['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    # 확률 버블 3개
    st.markdown(f"""
    <div class="prob-section">
        <div class="prob-bubble">
            <div class="prob-pct" style="color:#6BCB77;">{prob_low:.1f}%</div>
            <div class="prob-label">Low · 낮음</div>
            <div class="prob-bar-wrap">
                <div class="prob-bar-fill" style="width:{prob_low:.1f}%; background:#6BCB77;"></div>
            </div>
        </div>
        <div class="prob-bubble">
            <div class="prob-pct" style="color:#FFD93D;">{prob_mid:.1f}%</div>
            <div class="prob-label">Medium · 보통</div>
            <div class="prob-bar-wrap">
                <div class="prob-bar-fill" style="width:{prob_mid:.1f}%; background:#FFD93D;"></div>
            </div>
        </div>
        <div class="prob-bubble">
            <div class="prob-pct" style="color:#FF6B6B;">{prob_high:.1f}%</div>
            <div class="prob-label">High · 높음</div>
            <div class="prob-bar-wrap">
                <div class="prob-bar-fill" style="width:{prob_high:.1f}%; background:#FF6B6B;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
