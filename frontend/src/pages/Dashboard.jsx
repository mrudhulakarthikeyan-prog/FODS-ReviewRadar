import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#16a37a', '#e45b68', '#e5a23b'];
export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { axios.get('/api/stats').then(r => setStats(r.data)).catch(() => setError('Unable to load dashboard data. Check that the backend is running.')); }, []);
  if (error) return <div className="card error">{error}</div>;
  if (!stats) return <div className="card">Loading dashboard…</div>;
  const total = stats.total_reviews || 0;
  const chartData = [{name:'Positive',value:stats.positive||0},{name:'Negative',value:stats.negative||0},{name:'Neutral',value:stats.neutral||0}];
  return <section className="page">
    <div className="page-heading"><div><p className="eyebrow">OVERVIEW</p><h1>Dashboard</h1><p>Understand customer sentiment across your uploaded reviews.</p></div></div>
    <div className="stats-grid">
      <div className="stat-card"><span>Total reviews</span><strong>{total}</strong><small>Uploaded customer reviews</small></div>
      <div className="stat-card positive"><span>Positive</span><strong>{stats.positive||0}</strong><small>Favourable sentiment</small></div>
      <div className="stat-card negative"><span>Negative</span><strong>{stats.negative||0}</strong><small>Unfavourable sentiment</small></div>
      <div className="stat-card neutral"><span>Neutral</span><strong>{stats.neutral||0}</strong><small>Neutral sentiment</small></div>
    </div>
    <div className="card"><h2>Sentiment distribution</h2>{total === 0 ? <div className="empty-state"><div>◷</div><h3>No review data yet</h3><p>Upload a customer review CSV and run sentiment analysis to see your results here.</p></div> : <div style={{width:'100%',height:320}}><ResponsiveContainer><PieChart><Pie data={chartData.filter(x=>x.value>0)} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={105} label>{chartData.map((entry,i)=><Cell key={entry.name} fill={COLORS[i]}/>)}</Pie><Tooltip/><Legend/></PieChart></ResponsiveContainer></div>}</div>
  </section>;
}
