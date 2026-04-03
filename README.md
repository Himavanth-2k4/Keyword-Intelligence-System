# Keyword Intelligence System

A modern web application that extracts keywords and keyphrases from text using both Rule-Based (TF-IDF) and ML-Powered (KeyBERT) techniques. Features automatic summarization and topic classification.

![Keyword Intelligence System](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.2.0-blue.svg)

## ✨ Features

- 📊 **Dual Keyword Extraction**
  - Rule-Based: TF-IDF vectorization
  - ML-Based: KeyBERT semantic extraction
  
- 💬 **Key Phrase Detection** using spaCy NLP

- 📝 **Text Summarization** with BART-large-CNN

- 🏷️ **Topic Classification** (8 categories: crime, business, politics, technology, health, fraud, terrorism, finance)

- 📄 **PDF Support** - Upload and analyze PDF documents

- 💾 **CSV Export** - Download results for further analysis

- 🎨 **Modern UI** - Clean, minimalistic design with collapsible sidebar

## 🚀 Quick Start

### Prerequisites

- **Python** 3.8 or higher
- **Node.js** 14 or higher
- **npm** or **yarn**

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Puneet902/genai.git
cd genai
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install npm dependencies
npm install
```

## 🏃 Running the Application

### Start Backend Server

```bash
# From the backend directory
cd backend
python main.py
```

The backend API will be available at `http://localhost:8000`

### Start Frontend Application

Open a **new terminal** window:

```bash
# From the frontend directory
cd frontend
npm start
```

The frontend will automatically open at `http://localhost:3000`

## 📖 Usage

1. **Enter Text**: Paste your article or document into the text area
2. **Upload PDF** (Optional): Click "Choose PDF file" to upload a PDF document
3. **Configure Settings**: Adjust the number of keywords (5-20) using the slider
4. **Advanced Options**: Enable to configure N-gram ranges
5. **Analyze**: Click the "Analyze" button to process your text
6. **View Results**: See extracted keywords, phrases, summary, and predicted topic
7. **Export**: Download results as CSV for further analysis

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **KeyBERT** - ML-based keyword extraction
- **spaCy** - Natural language processing
- **Transformers** - BART models for summarization & classification
- **scikit-learn** - TF-IDF vectorization
- **PyPDF** - PDF text extraction

### Frontend
- **React 18.2** - UI library
- **Axios** - HTTP client
- **Modern CSS** - Custom minimalistic design

## 📁 Project Structure

```
genaiproject/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── index.jsx       # React entry point
│   │   ├── index.css       # Application styles
│   │   └── api.js          # API client
│   └── package.json        # Node dependencies
├── app.py                  # Streamlit version (alternative)
└── README.md              # This file
```

## 🔧 Configuration

### Backend Configuration

The backend runs on `http://0.0.0.0:8000` by default. To change the port, modify `main.py`:

```python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=YOUR_PORT, reload=True)
```

### Frontend Configuration

To connect to a different backend URL, create a `.env` file in the frontend directory:

```
REACT_APP_API_URL=http://your-backend-url:port
```

## 📋 API Endpoints

### POST /extract
Extract keywords from text.

**Request Body:**
```json
{
  "text": "Your text here",
  "top_n": 10,
  "ng_min": 1,
  "ng_max": 3
}
```

**Response:**
```json
{
  "rule_keywords": ["keyword1", "keyword2", ...],
  "ml_keywords": ["keyword1", "keyword2", ...],
  "phrases": ["phrase1", "phrase2", ...],
  "summary": "Summary text...",
  "topic": ["predicted_topic"]
}
```

### POST /extract_pdf
Extract keywords from PDF file.

**Form Data:**
- `file`: PDF file
- `top_n`: Number of keywords (default: 10)
- `ng_min`: N-gram minimum (default: 1)
- `ng_max`: N-gram maximum (default: 3)

## 🐛 Troubleshooting

### Backend Issues

**Problem**: spaCy model not found
```bash
# Solution: Download the model
python -m spacy download en_core_web_sm
```

**Problem**: CUDA/PyTorch errors
```bash
# Solution: Install CPU-only version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Frontend Issues

**Problem**: Module not found errors
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Port 3000 already in use
```bash
# Solution: Use a different port
PORT=3001 npm start
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

**Puneet**
- GitHub: [@Puneet902](https://github.com/Puneet902)

## 🙏 Acknowledgments

- KeyBERT for semantic keyword extraction
- spaCy for NLP capabilities
- Hugging Face Transformers for summarization models
- FastAPI for the excellent web framework
- React for the UI framework

---

**Note**: First-time setup may take several minutes to download ML models (BART, sentence-transformers). Subsequent runs will be faster.
