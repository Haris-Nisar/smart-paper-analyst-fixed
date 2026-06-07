"""
themes.py - Custom CSS theming for Smart Academic Paper Analyst.
Implements glassmorphism, dark/light themes, and professional UI polish.
"""


DARK_THEME_CSS = """
<style>
/* ─── Google Fonts ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─── CSS Variables ────────────────────────────────────── */
:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-tertiary: #1a1f2e;
    --bg-card: rgba(255,255,255,0.04);
    --bg-card-hover: rgba(255,255,255,0.08);
    --bg-card-active: rgba(255,255,255,0.12);
    --border-color: rgba(255,255,255,0.08);
    --border-accent: rgba(99,179,237,0.3);
    --border-accent-strong: rgba(99,179,237,0.6);
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --text-soft: #475569;
    --accent-blue: #63b3ed;
    --accent-blue-light: #90cdf4;
    --accent-purple: #b794f4;
    --accent-teal: #4fd1c5;
    --accent-green: #68d391;
    --accent-green-light: #9ae6b4;
    --accent-orange: #f6ad55;
    --accent-red: #fc8181;
    --accent-yellow: #fbd38d;
    --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-2: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --gradient-3: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    --gradient-warm: linear-gradient(135deg, #f6ad55 0%, #f687b3 100%);
    --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.25);
    --shadow-md: 0 4px 20px rgba(0,0,0,0.35);
    --shadow-lg: 0 8px 40px rgba(0,0,0,0.45);
    --shadow-xl: 0 12px 60px rgba(0,0,0,0.5);
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 20px;
    --radius-2xl: 28px;
    --transition-fast: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-smooth: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ─── Global Reset ─────────────────────────────────────── */
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }

.stApp {
    background: linear-gradient(135deg, var(--bg-primary) 0%, #0d1125 100%);
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ─── Scrollbar (Premium Style) ────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { 
    background: rgba(99,179,237,0.25); 
    border-radius: 4px; 
    border: 2px solid transparent;
    background-clip: padding-box;
}
::-webkit-scrollbar-thumb:hover { 
    background: rgba(99,179,237,0.45);
    background-clip: padding-box;
}

/* ─── Sidebar (Premium) ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(13,17,23,0.8) 0%, rgba(17,24,39,0.8) 100%);
    border-right: 1px solid var(--border-color);
    padding-top: 0;
    backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

/* ─── Main Content Area ────────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem 4rem;
    max-width: 1200px;
}

/* ─── Headers (Premium Typography) ─────────────────────────────────── */
h1 { 
    font-size: 2.2rem !important; 
    font-weight: 800 !important; 
    color: var(--text-primary) !important; 
    letter-spacing: -0.6px;
    line-height: 1.2;
}
h2 { 
    font-size: 1.6rem !important; 
    font-weight: 700 !important; 
    color: var(--text-primary) !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.75rem !important;
}
h3 { 
    font-size: 1.25rem !important; 
    font-weight: 600 !important; 
    color: var(--text-secondary) !important; 
}

/* ─── Cards (Glassmorphism) ────────────────────────────── */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.75rem;
    margin: 0.75rem 0;
    transition: var(--transition-normal);
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,179,237,0.3), transparent);
}
.glass-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-accent);
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

/* ─── Metric Cards (Enhanced) ──────────────────────────── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    transition: var(--transition-normal);
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(99,179,237,0.1) 0%, transparent 70%);
    transition: var(--transition-normal);
}
.metric-card:hover {
    border-color: var(--border-accent-strong);
    box-shadow: var(--shadow-md);
    transform: translateY(-3px);
}
.metric-card:hover::before {
    right: -30%;
    top: -30%;
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    background: var(--gradient-2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: block;
    margin: 0.5rem 0;
}
.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 0.5rem;
    font-weight: 600;
}

/* ─── Chat Bubbles (Premium) ───────────────────────────── */
.chat-user-bubble {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 0 18px 18px 18px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 2rem 0.75rem auto;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    word-wrap: break-word;
    max-width: 70%;
    animation: slideInRight 0.3s var(--transition-fast);
}
.chat-ai-bubble {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 18px 18px 18px 4px;
    padding: 1rem 1.25rem;
    margin: 0.75rem auto 0.75rem 2rem;
    font-size: 0.95rem;
    line-height: 1.7;
    color: var(--text-primary);
    box-shadow: var(--shadow-sm);
    word-wrap: break-word;
    max-width: 70%;
    animation: slideInLeft 0.3s var(--transition-fast);
}
.chat-timestamp {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
    text-align: right;
}
.chat-source-badge {
    display: inline-block;
    background: rgba(99,179,237,0.15);
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 16px;
    padding: 0.2rem 0.75rem;
    font-size: 0.7rem;
    color: var(--accent-blue-light);
    margin: 0.25rem 0.2rem 0 0;
    font-weight: 500;
    transition: var(--transition-fast);
}
.chat-source-badge:hover {
    background: rgba(99,179,237,0.25);
    border-color: rgba(99,179,237,0.5);
    transform: translateY(-1px);
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

/* ─── Buttons (Premium) ────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.7rem 1.75rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px !important;
    transition: var(--transition-normal) !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3) !important;
    width: auto !important;
    position: relative;
    overflow: hidden;
}
.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255,255,255,0.3);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102,126,234,0.45) !important;
    opacity: 0.98 !important;
}
.stButton > button:active { 
    transform: translateY(0) !important;
    box-shadow: 0 2px 10px rgba(102,126,234,0.3) !important;
}

/* ─── Input Fields (Premium) ───────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #1a1f2e !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.85rem 1.1rem !important;
    transition: var(--transition-fast) !important;
    font-size: 0.95rem !important;
    caret-color: var(--accent-blue) !important;
    -webkit-text-fill-color: #e2e8f0 !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #64748b !important;
    opacity: 0.8 !important;
    -webkit-text-fill-color: #64748b !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--border-accent-strong) !important;
    box-shadow: 0 0 0 3px rgba(99,179,237,0.15) !important;
    background: #222a3c !important;
    color: #e2e8f0 !important;
    -webkit-text-fill-color: #e2e8f0 !important;
}

/* ─── Chat message text rendering ──────────────────────── */
.chat-user-message p,
.chat-user-message div,
[data-testid="chat-message"] p {
    color: inherit !important;
    line-height: 1.7 !important;
}
.chat-user-message,
.chat-assistant-message {
    white-space: pre-wrap !important;
    word-break: break-word !important;
}


/* ─── File Uploader (Premium) ──────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed rgba(99,179,237,0.3) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2rem !important;
    transition: var(--transition-normal) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(99,179,237,0.6) !important;
    background: rgba(99,179,237,0.05) !important;
}

/* ─── Select Box ───────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* ─── Expanders (Premium) ──────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    transition: var(--transition-fast) !important;
    padding: 0.75rem 1rem !important;
}
.streamlit-expanderHeader:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--border-accent) !important;
}
.streamlit-expanderContent {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border-color) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    padding: 1.25rem !important;
}

/* ─── Tabs (Premium) ───────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.35rem !important;
    gap: 0.35rem !important;
    border: 1px solid var(--border-color) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.25rem !important;
    transition: var(--transition-fast) !important;
    text-transform: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(102,126,234,0.2) !important;
}

/* ─── Alerts ───────────────────────────────────────────── */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: var(--radius-md) !important;
    font-size: 0.9rem !important;
    border-left: 3px solid !important;
    padding: 1rem 1.25rem !important;
}

/* ─── Progress Bar ─────────────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    border-radius: 4px !important;
    box-shadow: 0 0 10px rgba(102,126,234,0.4) !important;
}

/* ─── Dividers ─────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border-color) !important;
    margin: 1.75rem 0 !important;
}

/* ─── Markdown (Premium) ───────────────────────────────── */
.stMarkdown p { 
    color: var(--text-secondary); 
    line-height: 1.8; 
    margin: 0.5rem 0;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { 
    color: var(--text-primary) !important;
    margin: 1.25rem 0 0.5rem 0 !important;
}
.stMarkdown ul, .stMarkdown ol { 
    color: var(--text-secondary);
    line-height: 1.8;
}
.stMarkdown li { margin: 0.35rem 0; }
.stMarkdown code {
    background: rgba(99,179,237,0.12) !important;
    color: var(--accent-blue-light) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.15rem 0.5rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border: 1px solid rgba(99,179,237,0.2) !important;
}

/* ─── Page Title Bar (Premium) ────────────────────────── */
.page-header {
    background: linear-gradient(135deg, rgba(102,126,234,0.12) 0%, rgba(118,75,162,0.08) 100%);
    border: 1px solid var(--border-accent);
    border-radius: var(--radius-lg);
    padding: 1.75rem 2.25rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.page-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, rgba(102,126,234,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -5%;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(118,75,162,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0;
    position: relative;
    z-index: 1;
    letter-spacing: -0.5px;
}
.page-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
    position: relative;
    z-index: 1;
    font-weight: 400;
}

/* ─── Search Result Card ───────────────────────────────── */
.search-result-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-left: 3px solid var(--accent-blue);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 1.25rem;
    margin: 0.75rem 0;
    transition: var(--transition-normal);
    box-shadow: var(--shadow-sm);
}
.search-result-card:hover {
    background: var(--bg-card-hover);
    border-left-color: var(--accent-purple);
    transform: translateX(4px);
    box-shadow: var(--shadow-md);
}
.search-score-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(99,179,237,0.2), rgba(183,148,244,0.2));
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.85rem;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--accent-blue-light);
}

/* ─── Paper Badge ──────────────────────────────────────── */
.paper-badge {
    display: inline-block;
    background: rgba(104,211,145,0.15);
    border: 1px solid rgba(104,211,145,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.85rem;
    font-size: 0.75rem;
    color: var(--accent-green-light);
    margin-right: 0.5rem;
    font-weight: 600;
    transition: var(--transition-fast);
}
.paper-badge:hover {
    background: rgba(104,211,145,0.25);
    border-color: rgba(104,211,145,0.5);
}

/* ─── Status Pill ──────────────────────────────────────── */
.status-pill {
    display: inline-block;
    border-radius: 20px;
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: var(--transition-fast);
}
.status-ready {
    background: rgba(104,211,145,0.15);
    border: 1px solid rgba(104,211,145,0.3);
    color: var(--accent-green-light);
}
.status-ready:hover {
    background: rgba(104,211,145,0.25);
    border-color: rgba(104,211,145,0.5);
}
.status-empty {
    background: rgba(252,129,129,0.15);
    border: 1px solid rgba(252,129,129,0.3);
    color: var(--accent-red);
}

/* ─── Spinner / Loader ─────────────────────────────────── */
.stSpinner > div { 
    border-top-color: var(--accent-blue) !important;
    border-width: 3px !important;
}

/* ─── Form Labels ──────────────────────────────────────── */
.stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    margin-bottom: 0.5rem !important;
}

/* ─── Sidebar Navigation ────────────────────────────────– */
.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.8rem 1.1rem;
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition-fast);
    margin: 0.2rem 0;
}
.nav-item:hover {
    background: var(--bg-card-hover);
    color: var(--text-primary);
}
.nav-item.active {
    background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(118,75,162,0.2));
    color: var(--accent-blue-light);
    border: 1px solid var(--border-accent);
}

.page-header::before {
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.page-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}
.page-subtitle {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
}

/* ─── Search Result Card ───────────────────────────────── */
.search-result-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-left: 3px solid var(--accent-blue);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    transition: all 0.2s ease;
}
.search-result-card:hover {
    background: var(--bg-card-hover);
    border-left-color: var(--accent-purple);
    transform: translateX(3px);
}
.search-score-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(99,179,237,0.2), rgba(183,148,244,0.2));
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 20px;
    padding: 0.15rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent-blue);
}

/* ─── Paper Badge ──────────────────────────────────────── */
.paper-badge {
    display: inline-block;
    background: rgba(107,179,126,0.15);
    border: 1px solid rgba(107,179,126,0.3);
    border-radius: 20px;
    padding: 0.15rem 0.75rem;
    font-size: 0.75rem;
    color: var(--accent-green);
    margin-right: 0.5rem;
}

/* ─── Upload Status ────────────────────────────────────── */
.upload-success {
    background: rgba(104,211,145,0.1);
    border: 1px solid rgba(104,211,145,0.3);
    border-radius: var(--radius-md);
    padding: 0.75rem 1rem;
    color: var(--accent-green);
    font-size: 0.9rem;
}
.upload-error {
    background: rgba(252,129,129,0.1);
    border: 1px solid rgba(252,129,129,0.3);
    border-radius: var(--radius-md);
    padding: 0.75rem 1rem;
    color: var(--accent-red);
    font-size: 0.9rem;
}

/* ─── Spinner / Loader ─────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* ─── Selectbox labels ─────────────────────────────────── */
.stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* ─── Sidebar Nav Button ───────────────────────────────── */
.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.7rem 1rem;
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    margin: 0.15rem 0;
    text-decoration: none;
}
.nav-item:hover { background: var(--bg-card-hover); color: var(--text-primary); }
.nav-item.active { background: linear-gradient(135deg,rgba(102,126,234,0.2),rgba(118,75,162,0.2)); color: var(--accent-blue); border: 1px solid rgba(102,126,234,0.2); }

/* ─── Index Status Pill ────────────────────────────────── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.status-ready { background: rgba(104,211,145,0.15); border: 1px solid rgba(104,211,145,0.3); color: #68d391; }
.status-empty { background: rgba(246,173,85,0.15); border: 1px solid rgba(246,173,85,0.3); color: #f6ad55; }

/* ─── Hide Streamlit branding ──────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
"""


LIGHT_THEME_CSS = """
<style>
:root {
    --bg-primary: #f8fafc;
    --bg-secondary: #f1f5f9;
    --bg-card: rgba(255,255,255,0.8);
    --bg-card-hover: rgba(255,255,255,0.95);
    --border-color: rgba(0,0,0,0.08);
    --border-accent: rgba(99,102,241,0.4);
    --text-primary: #1e293b;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --accent-blue: #6366f1;
    --accent-purple: #8b5cf6;
    --accent-teal: #0d9488;
    --accent-green: #059669;
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 20px rgba(0,0,0,0.12);
}
</style>
"""


def apply_theme(theme: str = "dark"):
    """Returns the CSS string for the selected theme."""
    if theme == "light":
        return DARK_THEME_CSS + LIGHT_THEME_CSS  # Extend dark base with light overrides
    return DARK_THEME_CSS
