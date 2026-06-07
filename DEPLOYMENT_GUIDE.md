# 🚀 SMART PAPER ANALYST — DEPLOYMENT & USAGE GUIDE

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** May 14, 2026  

---

## 📋 Quick Start

### 1. Prerequisites
```bash
# Ensure you have Python 3.8+ installed
python --version

# Ensure pip is up to date
pip install --upgrade pip
```

### 2. Install Dependencies
```bash
cd smart_paper_analyst
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Create/edit .env file in the project root
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
LLM_PROVIDER=openrouter
```

### 4. Run the Application
```bash
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## 🎯 How to Use

### Upload Papers
1. Click **"📤 Upload Research Papers"** in the sidebar
2. Select one or more PDF files
3. Click **"⚡ Process Papers"**
4. Wait for processing to complete (chunking, embedding, indexing)

### Ask Questions
1. Go to **"💬 AI Chat"** section
2. Choose from suggested questions (auto-generated per document type)
3. Or type your own question
4. Click **"Send ➤"** or press Enter
5. View the AI response with source citations

### Explore Features
- **📋 Summarize** — Get structured summaries of papers
- **⚖️ Compare** — Compare multiple papers side-by-side
- **🔭 Research Gaps** — Identify unexplored areas
- **🔍 Search** — Semantic search across all papers

---

## 🧠 Smart Features

### Document Type Detection
The app automatically detects document type and shows relevant questions:

**For Research Papers:**
- "What is the main objective of this research?"
- "What methodology was used?"
- "What are the key findings?"

**For Resumes:**
- "What skills are mentioned?"
- "Summarize the candidate's experience"
- "What technologies are listed?"

**For Reports:**
- "What is the executive summary?"
- "What recommendations are provided?"
- "What metrics are discussed?"

### Intelligent Retrieval
- Semantic search with 384-dimensional embeddings
- FAISS IndexFlatIP for fast similarity matching
- Optimized chunk sizes (1000 chars) for better context
- Top-8 most relevant chunks retrieved
- 10,000 character context window

### Multi-turn Conversation
- Chat history preserved within session
- Context-aware responses
- Source attribution for all answers
- Clear conversation flow

---

## ⚙️ Configuration

### Key Settings (in `utils/config.py`)

| Setting | Value | Purpose |
|---------|-------|---------|
| `CHUNK_SIZE` | 1000 | Text chunk size (~200 words) |
| `CHUNK_OVERLAP` | 150 | Overlap between chunks (~30 words) |
| `TOP_K_RETRIEVAL` | 8 | Number of chunks to retrieve |
| `SIMILARITY_THRESHOLD` | 0.0 | Min similarity score (0.0 = accept all) |
| `MAX_TOKENS` | 1024 | Max LLM response length |
| `TEMPERATURE` | 0.3 | LLM creativity (lower = more focused) |
| `MAX_FILE_SIZE_MB` | 50 | Max PDF file size |

### LLM Providers

**OpenRouter (Recommended)**
```
Provider: openrouter
Model: openai/gpt-4o-mini
API Key: OPENROUTER_API_KEY
Cost: $4.5e-06 per test request
Status: ✅ Tested & working
```

**Alternatives Available**
- Mistral AI (`mistral-small-latest`)
- HuggingFace Models (various)

---

## 📂 Project Structure

```
smart_paper_analyst/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Dependencies
├── .env                           # API keys (KEEP SECRET)
│
├── modules/
│   ├── pdf_processor.py           # PDF text extraction
│   ├── chunking.py                # Semantic text chunking
│   ├── embeddings.py              # FAISS vector store
│   ├── rag_pipeline.py            # RAG orchestration
│   ├── chatbot.py                 # Chat session management
│   ├── summarizer.py              # Paper summarization
│   ├── comparison.py              # Paper comparison
│   ├── research_gap.py            # Gap analysis
│   └── semantic_search.py         # Semantic search
│
├── ui/
│   ├── themes.py                  # CSS styling
│   ├── components.py              # Reusable UI components
│   └── sidebar.py                 # Navigation sidebar
│
├── utils/
│   ├── config.py                  # Configuration
│   ├── helpers.py                 # Utility functions
│   ├── prompts.py                 # LLM prompt templates
│   └── document_analyzer.py       # Document type detection
│
├── data/                          # Processed PDFs (temporary)
├── vector_store/                  # FAISS index & metadata
├── assets/                        # Images, logos
└── styles/                        # Additional stylesheets
```

---

## 🐛 Troubleshooting

### App won't start
**Error:** `streamlit run app.py` fails
**Solution:**
1. Check Python version: `python --version` (need 3.8+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check for syntax errors: `python -m py_compile app.py`

### Chat returns "No information found"
**Issue:** Retrieval not finding relevant content
**Solutions:**
1. Try different keywords
2. Ask more specific questions
3. Check that PDFs uploaded successfully
4. Look at terminal logs for retrieval scores

### API errors (404, 401, 429)
**404 - Model not found:**
- Check `OPENROUTER_MODEL` in `.env`
- Run `list_openrouter_models.py` to see available models

**401 - Invalid API key:**
- Check `OPENROUTER_API_KEY` in `.env`
- Verify key format: `sk-or-v1-...`
- Try creating a new API key

**429 - Rate limit:**
- Wait 1-2 minutes before retrying
- Upgrade API tier if recurring

### Chat input text invisible
**Issue:** Typed text doesn't show in input box
**Solution:**
- This has been fixed in the latest version
- Clear browser cache and reload
- Try different browser if persists

### Memory/Performance issues
**With large PDFs (>30MB):**
1. Reduce `CHUNK_SIZE` in config
2. Lower `TOP_K_RETRIEVAL`
3. Split PDF into smaller files
4. Increase system RAM

---

## 📊 Monitoring & Logs

### Terminal Logs
The app outputs detailed logs to terminal:
```
🔎 RAG Query: 'Your question here'
📊 Index status: 500 vectors, 50 chunks
✅ Retrieval returned 8 chunks
💬 Prompt length: 3500 chars
🤖 Calling LLM (openrouter)...
✅ LLM response: 450 chars
```

### Debug Information
In the UI, expand "📊 Debug: Retrieval Scores" to see:
- Retrieved chunk sources
- Similarity scores (0.0-1.0)
- Chunk word counts

### Performance Metrics
Watch for these on the dashboard:
- **Papers Loaded:** Should match uploaded count
- **Text Chunks:** Should increase after upload
- **Index Status:** Should show "Ready" after processing
- **LLM Provider:** Shows which API is active

---

## 🔒 Security Best Practices

### API Keys
```bash
# ✅ DO: Store in .env file (GITIGNORED)
# ❌ DON'T: Hardcode in Python files
# ❌ DON'T: Commit .env to Git
# ❌ DON'T: Share API keys in messages
```

### File Uploads
- Max file size: 50MB (configurable)
- Accepted format: PDF only
- Files processed locally, not uploaded externally
- Temporary files cleaned up after processing

### Data Privacy
- PDFs stored locally in `data/` directory
- Vector embeddings stored in `vector_store/`
- No data sent to external servers except API calls
- Clear "Clear All Papers" button to delete data

---

## 🚀 Performance Tips

### Faster Inference
1. **Reduce context size** — Fewer chunks = faster response
   ```python
   TOP_K_RETRIEVAL = 5  # Instead of 8
   ```

2. **Smaller chunks** — Faster embedding
   ```python
   CHUNK_SIZE = 500  # Instead of 1000
   ```

3. **Lower temperature** — Faster generation
   ```python
   TEMPERATURE = 0.1  # Instead of 0.3
   ```

### Better Quality
1. **Increase context** — More information for LLM
   ```python
   TOP_K_RETRIEVAL = 12  # Instead of 8
   ```

2. **Larger chunks** — Better semantic units
   ```python
   CHUNK_SIZE = 1500  # Instead of 1000
   ```

3. **Higher temperature** — More creative responses
   ```python
   TEMPERATURE = 0.7  # Instead of 0.3
   ```

---

## 📚 API Documentation

### OpenRouter API
- **Base URL:** https://openrouter.ai/api/v1
- **Endpoint:** POST `/chat/completions`
- **Models:** 363+ available (see `list_openrouter_models.py`)
- **Pricing:** Varies by model ($0 - $$$)
- **Docs:** https://openrouter.ai/docs

### Supported LLM Models
```
✅ openai/gpt-4o-mini          (RECOMMENDED - cheap & capable)
✅ mistralai/mistral-nemo      (Free tier available)
✅ meta-llama/llama-3.2-1b     (Free, fast)
✅ google/gemini-3.1-flash-lite (Fast, good quality)
```

---

## 🧪 Testing & Validation

### Run Tests
```bash
# Test API connection
python test_openrouter.py

# List available models
python list_openrouter_models.py

# Check Python syntax
python -m py_compile app.py
```

### Validation Checklist
- [ ] App starts without errors
- [ ] Can upload PDFs
- [ ] Can ask questions
- [ ] Responses show sources
- [ ] Suggested questions are relevant
- [ ] Chat input text is visible
- [ ] Dashboard metrics update

---

## 📞 Support

### Common Issues Checklist

| Issue | Cause | Fix |
|-------|-------|-----|
| App won't start | Missing deps | `pip install -r requirements.txt` |
| Chat text invisible | CSS bug | Fixed in v1.0 ✅ |
| "No papers indexed" | Upload failed | Check PDF format/size |
| API 404 error | Invalid model | Check model name in .env |
| Slow responses | Large context | Reduce TOP_K_RETRIEVAL |
| Memory issues | Large PDF | Split PDF or reduce CHUNK_SIZE |

### Getting Help
1. Check terminal logs for error messages
2. Verify `.env` configuration
3. Test API separately with `test_openrouter.py`
4. Check uploaded PDF is valid
5. Review error messages in chat interface

---

## 🎓 Understanding RAG

**RAG = Retrieval-Augmented Generation**

```
1. You ask a question
   ↓
2. Question is converted to embeddings (384-dim vector)
   ↓
3. FAISS searches for similar chunks (cosine similarity)
   ↓
4. Top 8 chunks retrieved
   ↓
5. Context assembled from chunks
   ↓
6. LLM generates answer using context
   ↓
7. Answer returned with source citations
```

**Why RAG?**
- Keeps answers grounded in actual documents
- Reduces hallucinations
- Provides source attribution
- Works with any PDF content

---

## 📈 Optimization Guide

### For Academic Papers
```python
CHUNK_SIZE = 1200       # Preserve paper structure
TOP_K_RETRIEVAL = 10    # More context for complex topics
TEMPERATURE = 0.2       # Precise, factual answers
```

### For Resumes
```python
CHUNK_SIZE = 800        # Keep sections intact
TOP_K_RETRIEVAL = 6     # Less redundancy needed
TEMPERATURE = 0.3       # Balance precision & naturalness
```

### For Reports
```python
CHUNK_SIZE = 1000       # Standard paragraph chunks
TOP_K_RETRIEVAL = 8     # Good balance
TEMPERATURE = 0.3       # Professional tone
```

---

## 🎉 Success Indicators

Your setup is working correctly when you see:

✅ **Dashboard Shows:**
- Papers Loaded: > 0
- Text Chunks: > 0
- Index Status: Ready
- LLM Provider: OpenRouter

✅ **Chat Works:**
- Suggested questions appear
- Questions are document-relevant
- LLM responds within 5 seconds
- Responses include sources

✅ **Performance:**
- Upload completes in < 30 seconds
- Chat response < 5 seconds
- No errors in terminal
- Clean UI rendering

---

## 🏁 You're Ready!

Your Smart Academic Paper Analyst is fully functional and ready to use. 

**Start by:**
1. Uploading a research paper or document
2. Asking one of the suggested questions
3. Exploring other features (summarize, compare, search)
4. Customizing settings as needed

**Questions?** Check logs, verify config, test API independently.

**Happy analyzing! 🚀**

---

**Made with ❤️ for researchers, students, and knowledge workers**

