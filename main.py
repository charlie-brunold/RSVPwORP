import pymupdf
import streamlit as st
import time

# --- Setup ---
st.set_page_config(page_title="Reader", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400;1,700&display=swap');
    .stApp {
        background-color: #F9F9F7;
        color: #1D1D1D;
    }
    .reader-card {
        background: #ffffff;
        border: 1px solid #E6E6E1;
        border-radius: 16px;
        padding: 60px 20px;
        margin: 20px 0;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 180px;
    }
    .orp-display {
        font-family: 'Atkinson Hyperlegible', sans-serif;
        font-size: 52px;
        display: flex;
        width: 100%;
    }
    .pivot { color: #D94343; font-weight: 700; }
    .prefix, .suffix { color: #1D1D1D; font-weight: 400; }

    /* Text visibility fixes */
    .stRadio label, .stRadio div[role="radiogroup"] label {
        color: #1D1D1D !important;
    }
    .stTextArea label, .stTextArea textarea {
        color: #1D1D1D !important;
    }
    .stTextArea textarea::placeholder {
        color: #666666 !important;
    }
    .stButton button {
        color: #1D1D1D !important;
        background-color: #ffffff !important;
        border: 1px solid #E6E6E1 !important;
    }
    .stButton button:hover {
        border-color: #D94343 !important;
    }
    label, p, span, div {
        color: #1D1D1D;
    }
    [data-testid="stHeader"], [data-testid="stFooter"] { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- State Management ---
if 'current_idx' not in st.session_state: st.session_state.current_idx = 0
if 'is_playing' not in st.session_state: st.session_state.is_playing = False
if 'word_corpus' not in st.session_state: st.session_state.word_corpus = []

def get_orp_parts(word):
    l = len(word)
    p = 0 if l <= 1 else (1 if l <= 5 else (2 if l <= 9 else 3))
    return word[:p], word[p], word[p+1:]

# --- Sidebar Controls ---
st.sidebar.title("Settings")
# We use a key for the slider so we can access it inside the loop
wpm = st.sidebar.select_slider(
    "Words Per Minute", 
    options=[200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000], 
    value=350,
    key="wpm_slider" 
)

# --- Main UI ---
st.markdown("<h3 style='text-align: center; color: #1D1D1D; margin-bottom: 20px;'>Reading Interface</h3>", unsafe_allow_html=True)

# Input method selector
input_method = st.radio("Choose input method:", ["Upload PDF", "Paste Text"], horizontal=True)

if input_method == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")

    if uploaded_file and not st.session_state.word_corpus:
        doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
        st.session_state.word_corpus = [w[4].strip() for p in doc for w in p.get_text("words") if w[4].strip()]
        st.session_state.current_idx = 0
        st.rerun()

else:  # Paste Text
    pasted_text = st.text_area("Paste your text here:", height=200, label_visibility="collapsed", placeholder="Paste your text here and click 'Load Text'")

    if st.button("Load Text") and pasted_text and not st.session_state.word_corpus:
        # Split text into words, removing empty strings
        st.session_state.word_corpus = [word.strip() for word in pasted_text.split() if word.strip()]
        st.session_state.current_idx = 0
        st.rerun()

if st.session_state.word_corpus:
    st.markdown('<div class="reader-card">', unsafe_allow_html=True)
    word_slot = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    progress = st.progress(st.session_state.current_idx / len(st.session_state.word_corpus))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Play / Pause"):
            st.session_state.is_playing = not st.session_state.is_playing
            st.rerun()
    with col2:
        if st.button("Restart"):
            st.session_state.current_idx = 0
            st.session_state.is_playing = False
            st.rerun()
    with col3:
        if st.button("Clear Text"):
            st.session_state.word_corpus = []
            st.session_state.current_idx = 0
            st.session_state.is_playing = False
            st.rerun()

    # --- The Active Loop ---
    if st.session_state.is_playing:
        while st.session_state.current_idx < len(st.session_state.word_corpus) and st.session_state.is_playing:
            word = st.session_state.word_corpus[st.session_state.current_idx]
            pre, piv, suf = get_orp_parts(word)
            
            # 1. Render Word
            word_slot.markdown(f"""
                <div class="orp-display">
                    <div style="width: 50%; text-align: right;" class="prefix">{pre}</div>
                    <div class="pivot">{piv}</div>
                    <div style="width: 50%; text-align: left;" class="suffix">{suf}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 2. Update Index & Progress
            st.session_state.current_idx += 1
            progress.progress(st.session_state.current_idx / len(st.session_state.word_corpus))
            
            # 3. Dynamic Delay (Slider check)
            # Fetching the WPM directly from session_state ensures it updates mid-loop
            current_wpm = st.session_state.wpm_slider
            iter_delay = 60 / current_wpm
            
            if word.endswith(('.', '!', '?')): iter_delay *= 2.0
            elif word.endswith(','): iter_delay *= 1.4
            
            time.sleep(iter_delay)
            
            # Safety check to stop loop if button is clicked (Rerun is needed for UI sync)
            if not st.session_state.is_playing:
                st.rerun()
    else:
        # Static Paused State
        word = st.session_state.word_corpus[st.session_state.current_idx]
        pre, piv, suf = get_orp_parts(word)
        word_slot.markdown(f"""
            <div class="orp-display" style="opacity: 0.4;">
                <div style="width: 50%; text-align: right;" class="prefix">{pre}</div>
                <div class="pivot">{piv}</div>
                <div style="width: 50%; text-align: left;" class="suffix">{suf}</div>
            </div>
            """, unsafe_allow_html=True)