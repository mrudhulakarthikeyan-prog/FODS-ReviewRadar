import React, { useRef, useState } from 'react';
import axios from 'axios';

export default function UploadTraining() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [records, setRecords] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [metrics, setMetrics] = useState(null);
  const [busy, setBusy] = useState(false);
  const [training, setTraining] = useState(false);

  const chooseFile = (selected) => {
    if (!selected) return;
    setFile(selected); setRecords(0); setMessage(''); setError(''); setMetrics(null);
  };

  const upload = async () => {
    if (!file) return;
    setBusy(true); setError(''); setMessage('');
    const form = new FormData(); form.append('file', file);
    try {
      const res = await axios.post('/api/upload_training', form);
      setRecords(res.data.records); setMessage(res.data.message);
    } catch (err) { setError(err.response?.data?.error || 'Training CSV upload failed.'); }
    finally { setBusy(false); }
  };

  const train = async () => {
    setTraining(true); setError(''); setMetrics(null);
    try { const res = await axios.post('/api/train'); setMetrics(res.data); }
    catch (err) { setError(err.response?.data?.error || 'Model training failed.'); }
    finally { setTraining(false); }
  };

  return <section className="page">
    <div className="page-heading"><div><p className="eyebrow">MODEL SETUP</p><h1>Upload Training Data</h1><p>Upload labelled reviews to train your sentiment classifier.</p></div></div>
    <div className="card upload-card">
      <div className="upload-area" onClick={() => inputRef.current?.click()} onDragOver={e => e.preventDefault()} onDrop={e => {e.preventDefault(); chooseFile(e.dataTransfer.files[0]);}}>
        <div className="upload-icon">⇧</div><h3>{file ? file.name : 'Drop your training CSV here'}</h3><p>or click to browse · CSV format</p>
        <input ref={inputRef} hidden type="file" accept=".csv,text/csv" onChange={e => chooseFile(e.target.files[0])}/>
      </div>
      <p className="helper-text">Required columns: <code>review_text</code> and either <code>sentiment</code> or <code>rating</code>. Rating labels are mapped as 1–2 Negative, 3 Neutral, 4–5 Positive.</p>
      <button className="primary-button" disabled={!file || busy} onClick={upload}>{busy ? 'Uploading…' : 'Upload and Validate'}</button>
      {message && <p className="success">{message} ({records} records)</p>}
      {error && <p className="error">{error}</p>}
    </div>
    {records > 0 && <div className="card"><h2>Train your model</h2><p>Your training file passed validation. Start model training to evaluate the available classifiers.</p><button className="primary-button" onClick={train} disabled={training}>{training ? 'Training model…' : 'Train Model'}</button>
      {metrics && <div className="metrics-grid"><div><span>Selected model</span><strong>{metrics.best_model}</strong></div><div><span>Accuracy</span><strong>{(metrics.metrics.accuracy*100).toFixed(1)}%</strong></div><div><span>Precision</span><strong>{(metrics.metrics.precision*100).toFixed(1)}%</strong></div><div><span>Recall</span><strong>{(metrics.metrics.recall*100).toFixed(1)}%</strong></div><div><span>F1 score</span><strong>{(metrics.metrics.f1_score*100).toFixed(1)}%</strong></div></div>}
    </div>}
  </section>;
}
