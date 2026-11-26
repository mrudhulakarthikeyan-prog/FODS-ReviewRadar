import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Insights() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    axios.get('/api/insights').then(r => setData(r.data)).catch(() => setError('Unable to load customer insights.'));
  }, []);

  if (error) return <section className="page"><p className="error">{error}</p></section>;
  if (!data) return <section className="page"><div className="card">Preparing customer insights…</div></section>;
  if (!data.review_count) return <section className="page"><div className="page-heading"><div><p className="eyebrow">CUSTOMER VOICE</p><h1>Insights</h1><p>Understand the themes behind customer feedback.</p></div></div><div className="card empty-state"><h3>No analysed reviews yet</h3><p>Upload customer reviews and run sentiment analysis to generate insights.</p></div></section>;

  const keywordCard = (title, words) => <div className="card"><h2>{title}</h2>{words.length ? words.map(([word, count]) => <div className="keyword-row" key={word}><span>{word}</span><strong>{count}</strong></div>) : <p>No clear themes found yet.</p>}</div>;
  return <section className="page">
    <div className="page-heading"><div><p className="eyebrow">CUSTOMER VOICE</p><h1>Insights</h1><p>Key product themes, supporting feedback and areas to improve.</p></div></div>
    <div className="insight-summary"><strong>{data.review_count}</strong><span>reviews included in this analysis</span><strong>{data.aspects.length}</strong><span>product aspects identified</span><strong>{data.mismatches.length}</strong><span>rating–sentiment mismatches</span></div>
    <div className="insights-grid">{keywordCard('Common terms · Positive reviews', data.positive_keywords)}{keywordCard('Common terms · Negative reviews', data.negative_keywords)}</div>
    <div className="card"><h2>Product aspects</h2><p>Aspect sentiment is estimated from wording near each detected feature. Review the evidence before making business decisions.</p>
      {data.aspects.length ? <div className="table-wrap"><table><thead><tr><th>Aspect</th><th>Mentions</th><th>Positive</th><th>Negative</th><th>Neutral</th><th>Overall signal</th></tr></thead><tbody>{data.aspects.map(a => <tr key={a.aspect}><td>{a.aspect}</td><td>{a.mentions}</td><td className="positive-text">{a.positive}</td><td className="negative-text">{a.negative}</td><td>{a.neutral}</td><td><span className={`signal-pill ${a.dominant_sentiment.toLowerCase()}`}>{a.dominant_sentiment}</span></td></tr>)}</tbody></table></div> : <p>No product aspects were clearly mentioned in the uploaded reviews.</p>}
    </div>
    {data.aspects.some(a => a.evidence?.length) && <div className="card"><h2>Customer evidence</h2><p>Examples from the uploaded reviews that support the themes above.</p>{data.aspects.filter(a => a.evidence?.length).map(a => <div className="evidence-group" key={a.aspect}><h3>{a.aspect}</h3>{a.evidence.slice(0,2).map((t,i) => <blockquote key={i}>“{t}”</blockquote>)}</div>)}</div>}
    <div className="card"><h2>Suggested areas to review</h2>{data.recommendations.length ? data.recommendations.map((r,i) => <div className="recommendation" key={i}><strong>{r.title}</strong><p>{r.detail}</p></div>) : <p>Upload more detailed reviews to identify improvement opportunities.</p>}</div>
    <div className="card"><h2>Rating–sentiment mismatches</h2><p>These reviews have a star rating that differs from the sentiment predicted from their text. They are worth checking manually.</p>
      {data.mismatches.length ? data.mismatches.map((m,i) => <div className="mismatch-row" key={i}><div><strong>{m.product_name}</strong><p>Rating: {m.rating}/5 · Rating-based label: {m.expected_from_rating} · Text sentiment: {m.sentiment}</p><span>{m.review_text}</span></div></div>) : <p>No rating–sentiment mismatches were detected in the available rated reviews.</p>}
    </div>
  </section>;
}
