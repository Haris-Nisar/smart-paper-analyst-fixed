# 🔬 Smart Academic Paper Analyst

> A production-quality AI-powered research assistant for analyzing, summarizing, comparing,
> and exploring academic papers — built with RAG, FAISS, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-orange?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-green?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 **PDF Upload** | Upload one or multiple research papers |
| 💬 **AI Chat** | Multi-turn RAG-powered chat about your papers |
| 📋 **Summarization** | Structured 8-section academic summaries |
| ⚖️ **Paper Comparison** | AI-generated side-by-side paper analysis |
| 🔭 **Research Gaps** | Identify unexplored areas and future directions |
| 🔍 **Semantic Search** | Find content by meaning, not just keywords |
| 🎨 **Beautiful UI** | Glassmorphism dark theme, professional SaaS design |

---

## 🏗️ Architecture

```
PDF Upload → PyMuPDF Extraction → Text Cleaning
    ↓
RecursiveCharacterTextSplitter (500–700 word chunks, 100-word overlap)
    ↓
sentence-transformers/all-MiniLM-L6-v2 Embeddings
    ↓
FAISS IndexFlatIP (cosine similarity via inner product)
    ↓
User Query → Query Embedding → Top-K Retrieval → LLM Generation (RAG)
```

---

## 🚀 Quick Start

### 1. Clone / Download
```bash
git clone https://github.com/your-repo/smart-paper-analyst
cd smart-paper-analyst
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Copy `.env.example` to `.env` and add your LLM API key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

**Recommended:** [OpenRouter](https://openrouter.ai/) — free tier, many models.

### 5. Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## ⚙️ Configuration

Edit `utils/config.py` or `.env` to customize:

| Setting | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openrouter` | `openrouter` / `mistral` / `huggingface` |
| `OPENROUTER_MODEL` | `mistralai/mistral-7b-instruct` | Any OpenRouter model |
| `CHUNK_SIZE` | `2500` chars (~500w) | Text chunk size |
| `CHUNK_OVERLAP` | `400` chars | Overlap between chunks |
| `TOP_K_RETRIEVAL` | `5` | Chunks retrieved per query |
| `MAX_FILE_SIZE_MB` | `50` | Max PDF size |

---

## 📁 Project Structure

```
smart_paper_analyst/
├── app.py                   # Main Streamlit entry point + all pages
├── requirements.txt
├── .env.example
├── README.md
│
├── modules/
│   ├── pdf_processor.py     # PyMuPDF extraction
│   ├── chunking.py          # RecursiveCharacterTextSplitter
│   ├── embeddings.py        # Sentence-transformers + FAISS
│   ├── rag_pipeline.py      # RAG pipeline + LLM clients
│   ├── summarizer.py        # Structured summarization
│   ├── comparison.py        # Multi-paper comparison
│   ├── research_gap.py      # Gap analysis
│   ├── semantic_search.py   # Semantic search engine
│   └── chatbot.py           # Chat session management
│
├── utils/
│   ├── config.py            # All settings & API keys
│   ├── prompts.py           # LLM prompt templates
│   └── helpers.py           # Utility functions
│
├── ui/
│   ├── themes.py            # CSS glassmorphism theme
│   ├── components.py        # Reusable UI components
│   └── sidebar.py           # Sidebar navigation
│
├── data/                    # Temporary PDF data
└── vector_store/            # Saved FAISS index
```

---

## ☁️ Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in Streamlit Cloud dashboard:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-..."
   LLM_PROVIDER = "openrouter"
   ```

### HuggingFace Spaces
1. Create a new Space (Streamlit SDK)
2. Upload all files
3. Add `OPENROUTER_API_KEY` in Space Secrets

### Render
1. Create a new Web Service
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `streamlit run app.py --server.port $PORT`
4. Add environment variables in Render dashboard

---

## 🤖 Supported LLM Models via OpenRouter

| Model | Speed | Quality |
|---|---|---|
| `mistralai/mistral-7b-instruct` | ⚡ Fast | ★★★★ |
| `meta-llama/llama-3-8b-instruct` | ⚡ Fast | ★★★★ |
| `anthropic/claude-3-haiku` | ⚡ Fast | ★★★★★ |
| `google/gemma-2-9b-it` | ⚡ Fast | ★★★★ |

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ using Python, Streamlit, LangChain, FAISS, and sentence-transformers*
