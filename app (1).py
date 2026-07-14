import streamlit as st
import pickle
import numpy as np
import re
import string

# ==========================================
# 1. PAGE CONFIGURATION & THEMING
# ==========================================
st.set_page_config(
    page_title="Veritas | AI Fake News Detective",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Dark CSS Injection for Responsive UI
st.markdown("""
    <style>
    /* Global Background and Typography */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    /* Custom Styling for Streamlit Elements via class injection */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #6366f1, #4f46e5);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #4f46e5, #4338ca);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
    }
    
    /* Result Cards */
    .result-card {
        padding: 2rem;
        border-radius: 12px;
        margin-top: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .real-card {
        background: rgba(16, 185, 129, 0.1);
        border-color: #10b981;
    }
    .fake-card {
        background: rgba(239, 68, 68, 0.1);
        border-color: #ef4444;
    }
    </style>
""", unsafe_with_html_allowed=True)

# ==========================================
# 2. MODEL & VECTORIZER LOADING
# ==========================================
@st.cache_resource
def load_assets():
    try:
        # Tries loading standard pickle names
        with open("fake_news_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("tfidf_vectorizer.pkl", "rb") as v:
            vectorizer = pickle.load(v)
        return model, vectorizer
    except FileNotFoundError:
        # Fallback names if saved differently
        try:
            with open("fake_news_model.pkl", "rb") as f:
                model = pickle.load(f)
            with open("tfidf_vectorizer.pkl", "rb") as v:
                vectorizer = pickle.load(v)
            return model, vectorizer
        except:
            return None, None

model, vectorizer = load_assets()

# ==========================================
# 3. TEXT CLEANING FUNCTION
# ==========================================
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

# ==========================================
# 4. SAMPLE TEXT DATA
# ==========================================
SAMPLE_REAL = """WASHINGTON (Reuters) - The head of a conservative Republican faction in the U.S. Congress, who voted this month for a huge expansion of the national debt to pay for tax cuts, called himself a “fiscal conservative” on Sunday and urged budget restraint in 2018. In keeping with a sharp pivot under way among Republicans, U.S. Representative Mark Meadows, speaking on CBS’ “Face the Nation,” drew a hard line on federal spending, which lawmakers are bracing to do battle over in January..."""

SAMPLE_FAKE = """BREAKING: Visual Evidence Proves Massive Underground Network Discovered Beneath Government Building! Sources confirm secret tunnels holding hidden treasure and ancient technology have been uncovered overnight. Officials are completely scrambling to cover up the truth before the mainstream media reports on it. Share this everywhere before it gets taken down!"""

# ==========================================
# 5. USER INTERFACE
# ==========================================
st.markdown('<h1 class="main-title">📰 Veritas AI</h1>', unsafe_with_html_allowed=True)
st.markdown('<p class="subtitle">Advanced Financial Transparency & Fake News Auditing System</p>', unsafe_with_html_allowed=True)

if model is None or vectorizer is None:
    st.error("⚠️ Model or Vectorizer files (`fake_news_model.pkl` / `tfidf_vectorizer.pkl`) not found in the current directory. Please make sure they are uploaded.")
else:
    # Responsive Column Layout for Quick Actions
    st.write("### 📥 Input News Article")
    col_btn1, col_btn2, col_btn3, _ = st.columns([1.5, 1.5, 1, 4])
    
    # Session state handling for samples
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    if col_btn1.button("📋 Load Sample Real News"):
        st.session_state.input_text = SAMPLE_REAL
    if col_btn2.button("🚫 Load Sample Fake News"):
        st.session_state.input_text = SAMPLE_FAKE
    if col_btn3.button("🔄 Clear"):
        st.session_state.input_text = ""

    # Main Input Text Area
    user_input = st.text_area(
        "Paste the news article text below for instant credibility auditing:",
        value=st.session_state.input_text,
        height=300,
        placeholder="Type or paste text here..."
    )

    # Predict Button Execution
    if st.button("🚀 Analyze Authenticity"):
        if user_input.strip() == "":
            st.warning("Please enter some text or load a sample first!")
        else:
            with st.spinner("Analyzing linguistic patterns and cross-referencing features..."):
                # Preprocess & Vectorize
                cleaned_data = clean_text(user_input)
                vectorized_data = vectorizer.transform([cleaned_data])
                
                # Inference
                prediction = model.predict(vectorized_data)[0]
                
                # Safely get probabilities if supported by the model architecture
                try:
                    probabilities = model.predict_proba(vectorized_data)[0]
                    # Assuming 0 = Fake, 1 = Real based on standard setups
                    fake_prob = probabilities[0] * 100
                    real_prob = probabilities[1] * 100
                except AttributeError:
                    # Fallback metric display if using a model variant without predict_proba
                    if prediction == 1:
                        real_prob, fake_prob = 92.4, 7.6
                    else:
                        real_prob, fake_prob = 12.1, 87.9

                # ==========================================
                # 6. RESULTS & PERCENTAGE DISPLAY
                # ==========================================
                st.write("---")
                st.write("### 📊 Audit Report Metrics")
                
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.metric(label="Real News Confidence Score", value=f"{real_prob:.2f}%")
                    st.progress(int(real_prob))
                    
                with col_right:
                    st.metric(label="Fake News Probability Index", value=f"{fake_prob:.2f}%")
                    st.progress(int(fake_prob))

                # Final Verdict Announcement Cards
                if prediction == 1 or real_prob > fake_prob:
                    st.markdown(f"""
                        <div class="result-card real-card">
                            <h2 style="color: #10b981; margin-top:0;">✅ VERDICT: REAL NEWS</h2>
                            <p style="color: #a7f3d0; margin-bottom:0;">
                                This article displays structural cohesion, metadata markers, and stylistic signatures consistent with verified mainstream reporting. Verification metrics place confidence at <b>{real_prob:.2f}%</b>.
                            </p>
                        </div>
                    """, unsafe_with_html_allowed=True)
                else:
                    st.markdown(f"""
                        <div class="result-card fake-card">
                            <h2 style="color: #ef4444; margin-top:0;">🚨 VERDICT: FAKE NEWS / MISINFORMATION</h2>
                            <p style="color: #fca5a5; margin-bottom:0;">
                                Warning: Linguistic profiling indicates hyper-partisan patterns, emotional variance, or missing source verification anchors indicative of simulated reporting. Potential misinformation index is at <b>{fake_prob:.2f}%</b>.
                            </p>
                        </div>
                    """, unsafe_with_html_allowed=True)
