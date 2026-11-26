import React, { useRef, useState } from 'react';
import axios from 'axios';

export default function UploadReviews() {
  const inputRef = useRef(null);
  const [file,setFile]=useState(null), [message,setMessage]=useState(''), [error,setError]=useState(''), [records,setRecords]=useState(0), [loading,setLoading]=useState(false), [analysing,setAnalysing]=useState(false);
  const upload = async () => {
    if(!file) return;
    setLoading(true); setError(''); setMessage('');
    const form=new FormData(); form.append('file',file);
    try { const res=await axios.post('/api/upload_reviews',form); setMessage(res.data.message); setRecords(res.data.records); }
    catch(e){setError(e.response?.data?.error||'Upload failed.');}
    finally{setLoading(false);}
  };
  const analyse = async () => {
    setAnalysing(true); setError('');
    try { const res=await axios.post('/api/run_predictions'); setMessage(res.data.message); }
    catch(e){setError(e.response?.data?.error||'Analysis failed.');}
    finally{setAnalysing(false);}
  };
  return <section className="page"><div className="page-heading"><div><p className="eyebrow">CUSTOMER DATA</p><h1>Upload Customer Reviews</h1><p>Import the reviews you want ReviewRadar to analyse.</p></div></div>
    <div className="card"><div className="upload-area" onClick={()=>inputRef.current?.click()} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();setFile(e.dataTransfer.files[0]);}}><div className="upload-icon">⇧</div><h3>{file?file.name:'Drop your customer review CSV here'}</h3><p>or click to browse · CSV format</p><input ref={inputRef} hidden type="file" accept=".csv" onChange={e=>setFile(e.target.files[0])}/></div><p className="helper-text">Required column: <code>review_text</code>. Optional columns: <code>product_name</code> and <code>rating</code>.</p><button className="primary-button" disabled={!file||loading} onClick={upload}>{loading?'Uploading…':'Upload Reviews'}</button>
      {message&&<p className="success">{message} {records>0?`(${records} reviews)` : ''}</p>}{error&&<p className="error">{error}</p>}
    </div>
    <div className="card"><h2>Run sentiment analysis</h2><p>After uploading customer reviews, use your trained model to classify all pending reviews.</p><button className="primary-button" onClick={analyse} disabled={analysing}>{analysing?'Analysing…':'Analyse Uploaded Reviews'}</button></div>
  </section>;
}
