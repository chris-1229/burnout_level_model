import streamlit as st
import pandas as pd
import pickle

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(page_title="번아웃 위험도 예측기", page_icon="🔥", layout="centered")

st.title("🔥 번아웃 위험도 예측기")
st.markdown("생성형 AI 사용 패턴과 심리 상태를 입력하면 번아웃 위험도를 예측합니다.")
st.divider()

# ── 모델 로드 ─────────────────────────────────────────────────
# pickle로 저장된 모델/스케일러를 불러옵니다.
# 같은 디렉토리에 model.pkl, scaler.pkl이 있어야 합니다.
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
    st.warning("⚠️ model.pkl 또는 scaler.pkl 파일을 찾을 수 없습니다. 데모 모드로 실행됩니다.")
    model_loaded = False

burnout_mapping = {"High": 2, "Medium": 1, "Low": 0}
reverse_burnout_mapping = {v: k for k, v in burnout_mapping.items()}

# ── 입력 UI ──────────────────────────────────────────────────
st.subheader("📋 입력 정보")

col1, col2 = st.columns(2)

with col1:
    weekly_ai_hours = st.number_input(
        "주간 생성형 AI 사용시간 (시간)",
        min_value=0.0,
        max_value=168.0,
        value=10.0,
        step=0.5,
        help="일주일 동안 ChatGPT, Claude 등 생성형 AI를 사용한 총 시간",
    )

with col2:
    ai_dependency = st.slider(
        "체감 AI 의존도",
        min_value=1,
        max_value=7,
        value=4,
        help="1 = 전혀 의존하지 않음 / 7 = 매우 강하게 의존함",
    )

anxiety_level = st.slider(
    "시험 중 불안 수준",
    min_value=1,
    max_value=9,
    value=5,
    help="1 = 매우 낮음 / 9 = 매우 높음",
)

st.divider()

# ── 예측 ─────────────────────────────────────────────────────
LEVEL_CONFIG = {
    "Low":    {"emoji": "🟢", "color": "#28a745", "label": "낮음"},
    "Medium": {"emoji": "🟡", "color": "#ffc107", "label": "보통"},
    "High":   {"emoji": "🔴", "color": "#dc3545", "label": "높음"},
}

if st.button("🔍 번아웃 위험도 예측하기", use_container_width=True, type="primary"):
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
        # 데모: 단순 규칙 기반 더미 예측
        score = weekly_ai_hours / 20 + ai_dependency / 7 + anxiety_level / 9
        if score > 2.0:
            predicted_label, proba = "High",   [0.10, 0.25, 0.65]
        elif score > 1.2:
            predicted_label, proba = "Medium", [0.20, 0.55, 0.25]
        else:
            predicted_label, proba = "Low",    [0.70, 0.20, 0.10]

    cfg = LEVEL_CONFIG[predicted_label]

    # 결과 카드
    st.markdown(
        f"""
        <div style="
            background-color: {cfg['color']}22;
            border: 2px solid {cfg['color']};
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin-bottom: 16px;
        ">
            <div style="font-size: 3rem;">{cfg['emoji']}</div>
            <div style="font-size: 1.2rem; color: #555; margin-top: 4px;">예측 번아웃 위험도</div>
            <div style="font-size: 2.2rem; font-weight: bold; color: {cfg['color']};">
                {cfg['label']} ({predicted_label})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 확률 바
    st.subheader("📊 예측 확률")
    prob_low, prob_mid, prob_high = proba[0], proba[1], proba[2]

    st.markdown("🟢 **Low (낮음)**")
    st.progress(prob_low, text=f"{prob_low*100:.1f}%")

    st.markdown("🟡 **Medium (보통)**")
    st.progress(prob_mid, text=f"{prob_mid*100:.1f}%")

    st.markdown("🔴 **High (높음)**")
    st.progress(prob_high, text=f"{prob_high*100:.1f}%")