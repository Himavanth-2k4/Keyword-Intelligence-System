import streamlit as st
from keybert import KeyBERT
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import pandas as pd
import pypdf as PyPDF2
import re

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

st.set_page_config(page_title="Keyword Intelligence System", layout="wide")
st.title("Keyword & Keyphrase Intelligence System (Rule-Based + ML)")

st.sidebar.title("Settings")
top_n = st.sidebar.slider("Number of Keywords", 5, 20, 10)
ng_min = st.sidebar.selectbox("N-Gram Min", [1,2,3], index=0)
ng_max = st.sidebar.selectbox("N-Gram Max", [1,2,3], index=2)

pdf = st.file_uploader("Upload PDF (optional)", type=["pdf"])
text_input = st.text_area("Enter text", height=250)

def extract_text_from_pdf(pdf):
    reader = PyPDF2.PdfReader(pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

if pdf:
    text_input = extract_text_from_pdf(pdf)

if st.button("Process"):
    if text_input.strip():
        tfidf = TfidfVectorizer(stop_words="english", ngram_range=(ng_min,ng_max))
        tfidf_fit = tfidf.fit_transform([text_input])
        scores = dict(zip(tfidf.get_feature_names_out(), tfidf_fit.toarray()[0]))
        rule_keywords = sorted(scores, key=scores.get, reverse=True)[:top_n]

        bert_keywords = kw_model.extract_keywords(
            text_input,
            keyphrase_ngram_range=(ng_min,ng_max),
            stop_words="english",
            top_n=top_n
        )
        bert_keywords = [k[0] for k in bert_keywords]

        doc = nlp(text_input)
        phrases = [chunk.text for chunk in doc.noun_chunks][:20]

        summary = summarizer(text_input, max_length=120, min_length=40, do_sample=False)[0]['summary_text']

        topics = classifier(text_input, 
                            candidate_labels=["crime", "business", 
                                              "politics", "technology", 
                                              "health", "fraud", 
                                              "terrorism", "finance"])

        st.subheader("Rule-Based Keywords (TF-IDF)")
        st.write(rule_keywords)

        st.subheader("ML-Based Keywords (KeyBERT)")
        st.write(bert_keywords)

        st.subheader("Extracted Keyphrases")
        st.write(phrases)

        st.subheader("Summary")
        st.write(summary)

        st.subheader("Predicted Topic")
        st.write(topics["labels"][0])

        st.subheader("Highlighted Text")
        highlighted = text_input
        for k in bert_keywords:
            highlighted = re.sub(f"(?i){k}", f"**:red[{k}]**", highlighted)
        st.markdown(highlighted)

        df = pd.DataFrame({
            "Rule-Based Keywords": rule_keywords,
            "ML-Based Keywords": bert_keywords
        })

        st.subheader("Download Results")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "keywords.csv")

        st.subheader("Save to Dataset")
        st.session_state.setdefault("dataset", [])
        st.session_state.dataset.append({
            "text": text_input,
            "summary": summary,
            "topic": topics["labels"][0],
            "keywords": bert_keywords
        })
        st.write(pd.DataFrame(st.session_state.dataset))
