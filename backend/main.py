from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from keybert import KeyBERT
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import pypdf as PyPDF2
from io import BytesIO
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
models = {
    'nlp': None,
    'kw_model': None,
    'summarizer': None,
    'summarizer_tokenizer': None,
    'classifier': None
}


class ExtractRequest(BaseModel):
    text: Optional[str] = None
    top_n: int = 10
    ng_min: int = 1
    ng_max: int = 3
    stop_words: str = "english"
    topic_categories: Optional[List[str]] = None
    max_phrases: int = 20
    summary_max_length: int = 120
    summary_min_length: int = 40
    use_ml_keywords: bool = True
    use_rule_keywords: bool = True
    use_phrases: bool = True
    use_summary: bool = True
    use_topics: bool = True


def load_models():
    """Load all required models dynamically"""
    global models

    # Load spaCy model
    if models['nlp'] is None:
        try:
            models['nlp'] = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            models['nlp'] = None

    # Load KeyBERT model
    if models['kw_model'] is None:
        try:
            models['kw_model'] = KeyBERT()
        except Exception as e:
            print(f"Warning: Could not load KeyBERT model: {e}")
            models['kw_model'] = None

    # Load summarizer models
    if models['summarizer'] is None or models['summarizer_tokenizer'] is None:
        try:
            models['summarizer'] = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
            models['summarizer_tokenizer'] = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        except Exception as e:
            print(f"Warning: Could not load summarizer models: {e}")
            models['summarizer'] = None
            models['summarizer_tokenizer'] = None

    # Load classifier (will be loaded on demand with custom categories)
    models['classifier'] = None


@app.on_event("startup")
def startup_event():
    """Load models on startup"""
    load_models()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


@app.post("/extract")
async def extract(payload: ExtractRequest):
    """Extract keywords, phrases, summary, and topics from text with dynamic configuration"""
    if not payload.text or not payload.text.strip():
        return {"error": "No text provided"}

    # Ensure models are loaded
    load_models()

    text = payload.text.strip()
    result = {}

    # Validate parameters
    ng_min = max(1, payload.ng_min)
    ng_max = max(ng_min, payload.ng_max)
    top_n = max(1, payload.top_n)

    # Default topic categories if not provided
    topic_categories = payload.topic_categories or ["crime", "business", "politics", "technology", "health", "fraud", "terrorism", "finance"]

    # Rule-based keywords (TF-IDF)
    if payload.use_rule_keywords:
        try:
            tfidf = TfidfVectorizer(stop_words=payload.stop_words, ngram_range=(ng_min, ng_max))
            tfidf_fit = tfidf.fit_transform([text])
            scores = dict(zip(tfidf.get_feature_names_out(), tfidf_fit.toarray()[0]))
            result["rule_keywords"] = sorted(scores, key=scores.get, reverse=True)[:top_n]
        except Exception as e:
            print(f"Warning: TF-IDF extraction failed: {e}")
            result["rule_keywords"] = []

    # ML-based keywords (KeyBERT)
    if payload.use_ml_keywords and models['kw_model']:
        try:
            bert_keywords = models['kw_model'].extract_keywords(
                text,
                keyphrase_ngram_range=(ng_min, ng_max),
                stop_words=payload.stop_words,
                top_n=top_n
            )
            result["ml_keywords"] = [k[0] for k in bert_keywords]
        except Exception as e:
            print(f"Warning: KeyBERT extraction failed: {e}")
            result["ml_keywords"] = []
    else:
        result["ml_keywords"] = []

    # Extract phrases (spaCy)
    if payload.use_phrases and models['nlp']:
        try:
            doc = models['nlp'](text)
            phrases = [chunk.text for chunk in doc.noun_chunks][:payload.max_phrases]
            result["phrases"] = phrases
        except Exception as e:
            print(f"Warning: Phrase extraction failed: {e}")
            result["phrases"] = []
    else:
        result["phrases"] = []

    # Text summarization
    if payload.use_summary:
        try:
            if len(text) > 100 and models['summarizer'] and models['summarizer_tokenizer']:
                inputs = models['summarizer_tokenizer'].encode(
                    text[:1024],
                    return_tensors="pt",
                    max_length=1024,
                    truncation=True
                )
                summary_ids = models['summarizer'].generate(
                    inputs,
                    max_length=payload.summary_max_length,
                    min_length=payload.summary_min_length,
                    do_sample=False
                )
                summary = models['summarizer_tokenizer'].decode(summary_ids[0], skip_special_tokens=True)
                result["summary"] = summary
            else:
                # Fallback: return first part of text or full text if short
                result["summary"] = text if len(text) <= 100 else text[:100] + "..."
        except Exception as e:
            print(f"Warning: Summarization failed: {e}")
            result["summary"] = text[:100] + "..." if len(text) > 100 else text
    else:
        result["summary"] = ""

    # Topic classification
    if payload.use_topics and topic_categories:
        try:
            # Load classifier with custom categories if needed
            if models['classifier'] is None:
                models['classifier'] = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

            topics_result = models['classifier'](text[:512], candidate_labels=topic_categories)
            result["topics"] = topics_result.get("labels", [])
            result["topic_scores"] = topics_result.get("scores", [])
        except Exception as e:
            print(f"Warning: Topic classification failed: {e}")
            result["topics"] = []
            result["topic_scores"] = []
    else:
        result["topics"] = []
        result["topic_scores"] = []

    # Add metadata
    result["metadata"] = {
        "text_length": len(text),
        "parameters": {
            "top_n": top_n,
            "ng_min": ng_min,
            "ng_max": ng_max,
            "stop_words": payload.stop_words,
            "topic_categories_count": len(topic_categories),
            "max_phrases": payload.max_phrases,
            "summary_max_length": payload.summary_max_length,
            "summary_min_length": payload.summary_min_length
        },
        "features_used": {
            "rule_keywords": payload.use_rule_keywords,
            "ml_keywords": payload.use_ml_keywords,
            "phrases": payload.use_phrases,
            "summary": payload.use_summary,
            "topics": payload.use_topics
        }
    }

    return result


@app.post("/extract_pdf")
async def extract_pdf(
    file: UploadFile = File(...),
    top_n: int = Form(10),
    ng_min: int = Form(1),
    ng_max: int = Form(3),
    stop_words: str = Form("english"),
    topic_categories: Optional[str] = Form(None),
    max_phrases: int = Form(20),
    summary_max_length: int = Form(120),
    summary_min_length: int = Form(40),
    use_ml_keywords: bool = Form(True),
    use_rule_keywords: bool = Form(True),
    use_phrases: bool = Form(True),
    use_summary: bool = Form(True),
    use_topics: bool = Form(True)
):
    """Extract keywords, phrases, summary, and topics from PDF with dynamic configuration"""
    contents = await file.read()
    text = extract_text_from_pdf(contents)

    # Parse topic categories from string if provided
    parsed_topic_categories = None
    if topic_categories:
        try:
            parsed_topic_categories = [cat.strip() for cat in topic_categories.split(",") if cat.strip()]
        except:
            parsed_topic_categories = None

    req = ExtractRequest(
        text=text,
        top_n=top_n,
        ng_min=ng_min,
        ng_max=ng_max,
        stop_words=stop_words,
        topic_categories=parsed_topic_categories,
        max_phrases=max_phrases,
        summary_max_length=summary_max_length,
        summary_min_length=summary_min_length,
        use_ml_keywords=use_ml_keywords,
        use_rule_keywords=use_rule_keywords,
        use_phrases=use_phrases,
        use_summary=use_summary,
        use_topics=use_topics
    )
    return await extract(req)


@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "Keyword Intelligence API is running",
        "version": "2.0.0",
        "features": ["keyword_extraction", "phrase_extraction", "summarization", "topic_classification", "pdf_processing"],
        "endpoints": {
            "POST /extract": "Extract insights from text",
            "POST /extract_pdf": "Extract insights from PDF",
            "GET /health": "Health check",
            "GET /config": "Get available configurations"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = {}
    for model_name, model in models.items():
        model_status[model_name] = model is not None

    return {
        "status": "healthy" if all(model_status.values()) else "degraded",
        "models": model_status,
        "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime in production
    }


@app.get("/config")
async def get_config():
    """Get available configuration options"""
    return {
        "stop_words_options": ["english", None],
        "ngram_range": {"min": 1, "max": 5},
        "top_n_range": {"min": 1, "max": 50},
        "max_phrases_range": {"min": 1, "max": 100},
        "summary_length_range": {"min_length": 10, "max_length": 500},
        "default_topic_categories": ["crime", "business", "politics", "technology", "health", "fraud", "terrorism", "finance", "sports", "entertainment", "science", "education"],
        "features": {
            "rule_keywords": "TF-IDF based keyword extraction",
            "ml_keywords": "KeyBERT based keyword extraction",
            "phrases": "spaCy noun phrase extraction",
            "summary": "BART-based text summarization",
            "topics": "Zero-shot topic classification"
        }
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)