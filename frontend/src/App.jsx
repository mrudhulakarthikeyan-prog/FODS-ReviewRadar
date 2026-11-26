import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import UploadReviews from './pages/UploadReviews';
import SentimentAnalysis from './pages/SentimentAnalysis';
import Insights from './pages/Insights';
import Comparison from './pages/Comparison';
import Reports from './pages/Reports';
import './index.css';

const navItems = [
  { to: '/', label: 'Dashboard', icon: '▦', end: true },
  { to: '/upload-reviews', label: 'Upload Reviews', icon: '⇧' },
  { to: '/sentiment-analysis', label: 'Sentiment Analysis', icon: '◎' },
  { to: '/insights', label: 'Insights', icon: '✧' },
  { to: '/comparison', label: 'Comparison', icon: '▥' },
  { to: '/reports', label: 'Reports', icon: '↧' },
];
const titles = {
  '/': ['Workspace overview', 'Your customer intelligence at a glance'],
  '/upload-reviews': ['Customer data', 'Bring your product feedback together'],
  '/sentiment-analysis': ['Review intelligence', 'Understand the tone behind a customer review'],
  '/insights': ['Customer voice', 'Discover the themes shaping customer experience'],
  '/comparison': ['Product performance', 'Compare customer sentiment across products'],
  '/reports': ['Export centre', 'Turn your review analysis into shareable reports'],
};
function Shell() {
  const location = useLocation();
  const [eyebrow, subtitle] = titles[location.pathname] || titles['/'];
  return <div className="app-container">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">R</span><span>Review<span className="brand-light">Radar</span><small>PRODUCT INTELLIGENCE</small></span></div>
      <div className="nav-caption">WORKSPACE</div>
      <nav><ul>{navItems.map(item => <li key={item.to}><NavLink to={item.to} end={item.end}><span className="nav-icon">{item.icon}</span><span>{item.label}</span><span className="nav-arrow">›</span></NavLink></li>)}</ul></nav>
      <div className="sidebar-bottom"><div className="status-dot"></div><div><strong>Analysis workspace</strong><small>Local environment</small></div></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div><span className="topbar-label">REVIEWRADAR / {eyebrow.toUpperCase()}</span><p>{subtitle}</p></div><div className="topbar-badge"><span></span> Workspace active</div></header>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload-reviews" element={<UploadReviews />} />
        <Route path="/sentiment-analysis" element={<SentimentAnalysis />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/comparison" element={<Comparison />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
      <footer className="app-footer"><span>ReviewRadar</span><span>Customer feedback, made clearer.</span></footer>
    </main>
  </div>;
}
export default function App() { return <Router><Shell /></Router>; }
