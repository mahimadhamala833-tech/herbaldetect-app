import streamlit as st
import requests
from PIL import Image
import google.generativeai as genai
import json

# CONFIG
API_URL    = "https://facing-reunite-fretful.ngrok-free.dev/predict"
GEMINI_KEY = "AIzaSyDC6p5js0iO3VQcjMFAWPkaJ0FBW0E20HY"

st.set_page_config(page_title="Herbal Plant Classifier", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%);
    padding: 3rem 2rem; border-radius: 20px; text-align: center;
    margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(27,67,50,0.3);
}
.hero h1 { color: white; font-size: 2.8rem; font-weight: 700; margin: 0; }
.hero p  { color: #b7e4c7; font-size: 1.1rem; margin-top: 0.5rem; }

.plant-card {
    background: linear-gradient(135deg, #d8f3dc, #b7e4c7);
    border-radius: 16px; padding: 1.8rem;
    border-left: 6px solid #2d6a4f;
    box-shadow: 0 4px 20px rgba(45,106,79,0.15);
    margin-bottom: 1rem;
}
.plant-name { font-size: 2rem; font-weight: 700; color: #1b4332; margin: 0; }
.plant-sub  { font-size: 0.95rem; color: #40916c; margin-top: 0.3rem; }

.conf-card {
    background: white; border-radius: 16px; padding: 1.5rem;
    border: 2px solid #b7e4c7; text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 1rem;
}
.conf-number { font-size: 3rem; font-weight: 700; line-height: 1; }
.conf-label  { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.3rem; }

.info-card {
    background: white; border-radius: 16px; padding: 1.8rem;
    border: 2px solid #b7e4c7; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 1rem;
}
.info-title { font-size: 0.85rem; font-weight: 600; color: #2d6a4f;
              text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
.use-item {
    background: #f0faf4; border-radius: 10px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; border-left: 4px solid #52b788;
    color: #1b4332; font-size: 0.95rem; line-height: 1.5;
}
.stProgress > div > div { background-color: #2d6a4f !important; }
div[data-testid="stSidebar"] { background: #f0faf4; }
</style>
""", unsafe_allow_html=True)

# GEMINI FUNCTION
def get_plant_info(plant_name):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""For the medicinal plant "{plant_name}", return ONLY this JSON, no extra text:
{{
  "scientific_name": "full scientific name",
  "family": "plant family name",
  "origin": "place of origin",
  "parts_used": "which parts are used medicinally",
  "uses": [
    "use 1 with explanation",
    "use 2 with explanation",
    "use 3 with explanation",
    "use 4 with explanation"
  ],
  "precaution": "any safety warning or None"
}}"""
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except:
        return None

# SIDEBAR
with st.sidebar:
    st.markdown("### 🌿 Herbal Classifier")
    st.markdown("---")
    st.markdown("**Model:** EfficientNetB3")
    st.markdown("**Plants:** 30 classes")
    st.markdown("**platform:** Google colab")
    st.markdown("---")
    if st.button("🔗 Check API Connection", use_container_width=True):
        try:
            r = requests.get(API_URL.replace("/predict", "/health"), timeout=10)
            if r.status_code == 200:
                st.success(f"✅ Connected!\n{r.json().get('total_classes')} plants ready.")
            else:
                st.error("❌ Not responding")
        except:
            st.error("❌ Cannot reach API.\nIs Colab Cell 11 running?")
    st.markdown("---")
    st.caption("Built with EfficientNetB3\nPowered by Google Colab +A WBL project by Mahima dhamala")

# HERO
st.markdown("""
<div class="hero">
    <h1>🌿 Herbal Plant Classifier</h1>
    <p>Upload a plant leaf image — AI identifies the species and reveals its medicinal secrets</p>
</div>
""", unsafe_allow_html=True)

# UPLOAD
uploaded_file = st.file_uploader(
    "📤 Upload a plant leaf image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload a clear photo of a plant leaf for best results"
)

if uploaded_file:
    col_img, col_res = st.columns([1, 1.4], gap="large")

    with col_img:
        st.markdown("**📷 Uploaded Image**")
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        st.caption(f"{uploaded_file.name}  |  {img.size[0]}×{img.size[1]} px")

    with col_res:
        with st.spinner("🔬 Analyzing plant with AI..."):
            try:
                uploaded_file.seek(0)
                r = requests.post(
                    API_URL,
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                    timeout=60
                )

                if r.status_code == 200:
                    res        = r.json()
                    conf       = res["confidence"]
                    plant_name = res["plant"]

                    # Plant name card
                    st.markdown(f"""
                    <div class="plant-card">
                        <div class="plant-name">🌱 {plant_name}</div>
                        <div class="plant-sub">Identified by EfficientNetB3 CNN</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Confidence card
                    color = "#2d6a4f" if conf > 80 else "#e67e22" if conf > 50 else "#e74c3c"
                    st.markdown(f"""
                    <div class="conf-card">
                        <div class="conf-number" style="color:{color};">{conf:.1f}%</div>
                        <div class="conf-label">Confidence Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(conf / 100)

                    # Gemini info
                    st.markdown("---")
                    with st.spinner("✨ Fetching info from Gemini AI..."):
                        info = get_plant_info(plant_name)

                    if info:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("🔬 Scientific Name", info.get("scientific_name", "N/A"))
                            st.metric("🌍 Origin", info.get("origin", "N/A"))
                        with c2:
                            st.metric("🌾 Family", info.get("family", "N/A"))
                            st.metric("💊 Parts Used", info.get("parts_used", "N/A"))

                        st.markdown("""<div class="info-card">
                            <div class="info-title">💊 Medicinal Uses</div>""",
                            unsafe_allow_html=True)
                        for use in info.get("uses", []):
                            st.markdown(f'<div class="use-item">✅ {use}</div>',
                                unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                        if info.get("precaution") and info["precaution"].lower() != "none":
                            st.warning(f"⚠️ **Precaution:** {info['precaution']}")
                    else:
                        st.markdown(f"""<div class="info-card">
                            <div class="info-title">💊 Medicinal Uses</div>
                            <div class="use-item">{res.get('description', 'No info available.')}</div>
                        </div>""", unsafe_allow_html=True)

                    # Top 3
                    st.markdown("---")
                    st.markdown("**📊 Top 3 Predictions**")
                    medals = ["🥇", "🥈", "🥉"]
                    for i, item in enumerate(res.get("top3", [])):
                        c = item["confidence"]
                        st.markdown(f"**{medals[i]} {item['plant']}** — {c:.1f}%")
                        st.progress(c / 100)

                else:
                    st.error(f"❌ API Error: {r.json().get('error', 'Unknown')}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect!\n\nMake sure Colab Cell 11 is still running.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; background:#f0faf4;
                border-radius:20px; border:2px dashed #b7e4c7; margin-top:1rem;">
        <div style="font-size:4rem;">🌿</div>
        <h3 style="color:#2d6a4f; margin:1rem 0 0.5rem;">Upload a Plant Image to Begin</h3>
        <p style="color:#74c69d;">Supports JPG, JPEG, PNG, WEBP</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#aaa; font-size:0.85rem; padding:1rem 0;">
    🌿 Herbal Plant Classifier &nbsp;·&nbsp; EfficientNetB3 &nbsp;·&nbsp;
    30 Medicinal Plants &nbsp;·&nbsp; Powered by Google Colab 
</div>
""", unsafe_allow_html=True)
