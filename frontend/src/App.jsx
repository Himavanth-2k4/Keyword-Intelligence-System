import React, { useState, useEffect } from 'react';
import { postExtract, postExtractPDF } from './api';

export default function App() {
    const [text, setText] = useState('');
    const [file, setFile] = useState(null);
    const [topN, setTopN] = useState(10);
    const [ngMin, setNgMin] = useState(1);
    const [ngMax, setNgMax] = useState(3);
    const [stopWords, setStopWords] = useState('english');
    const [topicCategories, setTopicCategories] = useState('');
    const [maxPhrases, setMaxPhrases] = useState(20);
    const [summaryMaxLength, setSummaryMaxLength] = useState(120);
    const [summaryMinLength, setSummaryMinLength] = useState(40);
    const [advanced, setAdvanced] = useState(false);
    const [expert, setExpert] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [theme, setTheme] = useState('light');
    const [config, setConfig] = useState(null);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    // Load configuration on mount
    useEffect(() => {
        const loadConfig = async () => {
            try {
                const response = await fetch('http://localhost:8000/config');
                const configData = await response.json();
                setConfig(configData);
            } catch (error) {
                console.error('Failed to load config:', error);
            }
        };
        loadConfig();
    }, []);

    const submit = async () => {
        setLoading(true);
        setResult(null);
        try {
            const payload = {
                text,
                top_n: topN,
                ng_min: ngMin,
                ng_max: ngMax,
                stop_words: stopWords,
                topic_categories: topicCategories ? topicCategories.split(',').map(cat => cat.trim()) : null,
                max_phrases: maxPhrases,
                summary_max_length: summaryMaxLength,
                summary_min_length: summaryMinLength,
                use_ml_keywords: true,
                use_rule_keywords: true,
                use_phrases: true,
                use_summary: true,
                use_topics: true
            };

            if (file) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('top_n', topN);
                formData.append('ng_min', ngMin);
                formData.append('ng_max', ngMax);
                formData.append('stop_words', stopWords);
                if (topicCategories) formData.append('topic_categories', topicCategories);
                formData.append('max_phrases', maxPhrases);
                formData.append('summary_max_length', summaryMaxLength);
                formData.append('summary_min_length', summaryMinLength);
                formData.append('use_ml_keywords', 'true');
                formData.append('use_rule_keywords', 'true');
                formData.append('use_phrases', 'true');
                formData.append('use_summary', 'true');
                formData.append('use_topics', 'true');
                const data = await postExtractPDF(formData);
                setResult(data);
            } else if (text.trim()) {
                const data = await postExtract(payload);
                setResult(data);
            }
        } catch (err) {
            console.error(err);
            alert('Error processing request. Make sure backend is running.');
        }
        setLoading(false);
    };

    const downloadCSV = () => {
        if (!result) return;
        const rows = [
            ['Rule-Based Keywords', 'ML-Based Keywords'],
            ...result.rule_keywords.map((r, i) => [r, result.ml_keywords[i] || ''])
        ];
        const csv = rows.map(r => r.join(',')).join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'keywords.csv';
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className={`app-root ${theme}`}>
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo">
                        <h2>Keyword Intelligence</h2>
                    </div>
                    <button
                        className="theme-toggle"
                        onClick={() => setTheme(prev => (prev === 'light' ? 'dark' : 'light'))}
                        aria-label="Toggle theme"
                    >
                        Theme: {theme}
                    </button>
                </div>

                <div className="settings">
                    <h3>Settings</h3>

                    <div className="setting-group">
                        <label>Top Keywords ({topN})</label>
                        <input
                            type="range"
                            min="5"
                            max="50"
                            value={topN}
                            onChange={e => setTopN(Number(e.target.value))}
                            className="slider"
                        />
                    </div>

                    <div className="setting-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={advanced}
                                onChange={() => setAdvanced(a => !a)}
                            />
                            <span>Advanced Options</span>
                        </label>
                    </div>

                    {advanced && (
                        <div className="advanced-settings">
                            <div className="setting-group">
                                <label>N-gram Min</label>
                                <select value={ngMin} onChange={e => setNgMin(Number(e.target.value))}>
                                    <option value={1}>1</option>
                                    <option value={2}>2</option>
                                    <option value={3}>3</option>
                                    <option value={4}>4</option>
                                    <option value={5}>5</option>
                                </select>
                            </div>

                            <div className="setting-group">
                                <label>N-gram Max</label>
                                <select value={ngMax} onChange={e => setNgMax(Number(e.target.value))}>
                                    <option value={1}>1</option>
                                    <option value={2}>2</option>
                                    <option value={3}>3</option>
                                    <option value={4}>4</option>
                                    <option value={5}>5</option>
                                </select>
                            </div>

                            <div className="setting-group">
                                <label>Stop Words</label>
                                <select value={stopWords} onChange={e => setStopWords(e.target.value)}>
                                    <option value="english">English</option>
                                    <option value="">None</option>
                                </select>
                            </div>

                            <div className="setting-group">
                                <label>Max Phrases ({maxPhrases})</label>
                                <input
                                    type="range"
                                    min="5"
                                    max="100"
                                    value={maxPhrases}
                                    onChange={e => setMaxPhrases(Number(e.target.value))}
                                    className="slider"
                                />
                            </div>

                            <div className="setting-group">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        checked={expert}
                                        onChange={() => setExpert(e => !e)}
                                    />
                                    <span>Expert Options</span>
                                </label>
                            </div>
                        </div>
                    )}

                    {expert && (
                        <div className="expert-settings">
                            <div className="setting-group">
                                <label>Summary Min Length ({summaryMinLength})</label>
                                <input
                                    type="range"
                                    min="10"
                                    max="100"
                                    value={summaryMinLength}
                                    onChange={e => setSummaryMinLength(Number(e.target.value))}
                                    className="slider"
                                />
                            </div>

                            <div className="setting-group">
                                <label>Summary Max Length ({summaryMaxLength})</label>
                                <input
                                    type="range"
                                    min="50"
                                    max="500"
                                    value={summaryMaxLength}
                                    onChange={e => setSummaryMaxLength(Number(e.target.value))}
                                    className="slider"
                                />
                            </div>

                            <div className="setting-group">
                                <label>Topic Categories</label>
                                <textarea
                                    value={topicCategories}
                                    onChange={e => setTopicCategories(e.target.value)}
                                    placeholder="crime, business, politics, technology, health, fraud, terrorism, finance (comma-separated)"
                                    className="topic-input"
                                    rows="3"
                                />
                                <small className="help-text">Leave empty for defaults</small>
                            </div>
                        </div>
                    )}
                </div>
            </aside>

            <main className="main">
                <div className="main-header">
                    <h1>Keyword & Keyphrase Intelligence</h1>
                    <p className="subtitle">Extract insights using TF-IDF and KeyBERT</p>
                </div>

                <div className="input-section">
                    <textarea
                        value={text}
                        onChange={e => setText(e.target.value)}
                        placeholder="Paste your article, document, or any text here for analysis..."
                        className="text-input"
                    />

                    <div className="action-bar">
                        <div className="file-upload-wrapper">
                            <input
                                type="file"
                                accept="application/pdf"
                                id="pdf-upload"
                                onChange={e => setFile(e.target.files[0])}
                                className="file-input"
                            />
                            <label htmlFor="pdf-upload" className="file-label">
                                {file ? file.name : 'Choose PDF file'}
                            </label>
                        </div>

                        <div className="button-group">
                            <button onClick={submit} disabled={loading} className="btn-primary">
                                {loading ? 'Processing...' : 'Analyze'}
                            </button>
                            <button onClick={downloadCSV} disabled={!result} className="btn-secondary">
                                Export CSV
                            </button>
                        </div>
                    </div>
                </div>

                {result && (
                    <section className="results">
                        <div className="card">
                            <div className="card-header">
                                <h3>Rule-Based Keywords</h3>
                                <span className="badge">TF-IDF</span>
                            </div>
                            <ul className="keyword-list">
                                {(result.rule_keywords || []).map((k, i) => (
                                    <li key={i} className="keyword-item">{k}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="card">
                            <div className="card-header">
                                <h3>ML-Based Keywords</h3>
                                <span className="badge">KeyBERT</span>
                            </div>
                            <ul className="keyword-list">
                                {(result.ml_keywords || []).map((k, i) => (
                                    <li key={i} className="keyword-item">{k}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="card">
                            <div className="card-header">
                                <h3>Key Phrases</h3>
                                <span className="badge">spaCy</span>
                            </div>
                            <ul className="keyword-list">
                                {(result.phrases || []).map((k, i) => (
                                    <li key={i} className="keyword-item">{k}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="card summary-card">
                            <div className="card-header">
                                <h3>Summary & Topics</h3>
                            </div>
                            <p className="summary-text">{result.summary}</p>
                            {result.topics && result.topics.length > 0 && (
                                <div className="topics-section">
                                    <div className="topic-badge">
                                        <span className="topic-label">Primary Topic:</span>
                                        <span className="topic-value">{result.topics[0]}</span>
                                        {result.topic_scores && result.topic_scores[0] && (
                                            <span className="topic-score">({(result.topic_scores[0] * 100).toFixed(1)}%)</span>
                                        )}
                                    </div>
                                    {result.topics.length > 1 && (
                                        <div className="secondary-topics">
                                            <span className="topic-label">Other Topics:</span>
                                            <div className="topic-list">
                                                {result.topics.slice(1, 4).map((topic, i) => (
                                                    <span key={i} className="secondary-topic">
                                                        {topic}
                                                        {result.topic_scores && result.topic_scores[i + 1] && (
                                                            <span className="topic-score-small">({(result.topic_scores[i + 1] * 100).toFixed(1)}%)</span>
                                                        )}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {result.metadata && (
                            <div className="card">
                                <div className="card-header">
                                    <h3>Analysis Metadata</h3>
                                </div>
                                <div className="metadata-content">
                                    <div className="metadata-item">
                                        <span className="metadata-label">Text Length:</span>
                                        <span className="metadata-value">{result.metadata.text_length} characters</span>
                                    </div>
                                    <div className="metadata-item">
                                        <span className="metadata-label">Parameters:</span>
                                        <span className="metadata-value">
                                            Top {result.metadata.parameters?.top_n || 'N/A'} keywords,
                                            N-grams ({result.metadata.parameters?.ng_min || 'N/A'}-{result.metadata.parameters?.ng_max || 'N/A'})
                                        </span>
                                    </div>
                                    <div className="metadata-item">
                                        <span className="metadata-label">Features Used:</span>
                                        <span className="metadata-value">
                                            {Object.entries(result.metadata.features_used || {})
                                                .filter(([_, enabled]) => enabled)
                                                .map(([feature, _]) => feature.replace('_', ' '))
                                                .join(', ')}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </section>
                )}
            </main>
        </div>
    );
}