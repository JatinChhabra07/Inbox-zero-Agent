import { useState, useEffect } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import { motion, AnimatePresence, useMotionValue, useMotionTemplate } from 'framer-motion';
import { Mail, RefreshCw, LogOut, Shield, Zap } from 'lucide-react';
import './App.css';

// ✨ NEW: The "Cyber-Aurora" Background
const AuroraBackground = () => {
  return (
    <div className="aurora-container">
      <div className="aurora-blob blob-purple"></div>
      <div className="aurora-blob blob-cyan"></div>
      <div className="aurora-blob blob-blue"></div>
      <div className="aurora-grid"></div> {/* Tech grid overlay */}
    </div>
  );
};

function App() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  
  // Mouse Spotlight Logic
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  function handleMouseMove({ clientX, clientY }: { clientX: number, clientY: number }) {
    mouseX.set(clientX);
    mouseY.set(clientY);
  }

  // Persistence
  useEffect(() => {
    const savedUser = localStorage.getItem('inbox_zero_user');
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  const googleLogin = useGoogleLogin({
    flow: 'auth-code',
    scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose',
    onSuccess: async (codeResponse) => {
      setLoading(true);
      try {
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/google`, { code: codeResponse.code });
        setUser(res.data.user);
        localStorage.setItem('inbox_zero_user', JSON.stringify(res.data.user));
      } catch (error) {
        console.error("Login failed:", error);
        alert("Login failed!");
      } finally {
        setLoading(false);
      }
    },
    onError: errorResponse => console.log(errorResponse),
  });

  const logout = () => {
    setUser(null);
    localStorage.removeItem('inbox_zero_user');
    setLogs([]);
  };

  const runAgent = async () => {
    if (!user) return;
    setLoading(true);
    setLogs(["🚀 Agent starting...", "🔍 Scanning inbox (Batch 5)..."]);
    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/run-agent`, { email: user.email });
      setLogs(prev => [...prev, "✅ Batch processing complete!", ...res.data.agent_response.split('\n')]);
    } catch (error: any) {
      console.error("Agent failed:", error);
      setLogs(prev => [...prev, "❌ Error: Agent crashed."]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-wrapper" onMouseMove={handleMouseMove}>
      {/* 🌌 FULL SCREEN AURORA BACKGROUND */}
      <AuroraBackground />

      {/* 💡 Mouse Spotlight Layer */}
      <motion.div
        className="spotlight-layer"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              600px circle at ${mouseX}px ${mouseY}px,
              rgba(255, 255, 255, 0.03),
              transparent 80%
            )
          `,
        }}
      />

      <div className="app-container">
        {/* 🃏 THE GLASS CARD */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.6, type: "spring", bounce: 0.3 }}
          className="card"
        >
          <div className="header">
            <div className="icon-wrapper">
              <Mail size={28} color="#fff" />
            </div>
            <div>
              <h1>Inbox Zero Agent</h1>
              <p className="subtitle">Autonomous Email Intelligence</p>
            </div>
          </div>
          
          <AnimatePresence mode="wait">
            {!user ? (
              <motion.div 
                key="login"
                initial={{ opacity: 0, filter: 'blur(10px)' }}
                animate={{ opacity: 1, filter: 'blur(0px)' }}
                exit={{ opacity: 0, filter: 'blur(10px)' }}
                className="login-section"
              >
                <div className="feature-grid">
                  <div className="feature-item"><Shield className="feature-icon" /><span>Secure OAuth 2.0</span></div>
                  <div className="feature-item"><Zap className="feature-icon" /><span>Llama 3 AI Brain</span></div>
                </div>
                <button onClick={() => googleLogin()} disabled={loading} className="btn-primary">
                  {loading ? "Establishing Link..." : "🚀 Initialize Connection"}
                </button>
              </motion.div>
            ) : (
              <motion.div 
                key="dashboard"
                initial={{ opacity: 0, filter: 'blur(10px)' }}
                animate={{ opacity: 1, filter: 'blur(0px)' }}
                className="dashboard"
              >
                <div className="user-info">
                  <div className="avatar-ring"><img src={user.picture} alt="Profile" className="avatar" /></div>
                  <div><h3>{user.name}</h3><span className="status-indicator">● Online :: Operative</span></div>
                </div>

                <div className="action-area">
                  <button onClick={runAgent} disabled={loading} className={`btn-action ${loading ? 'processing' : ''}`}>
                    {loading ? (<span className="loading-text"><RefreshCw className="spin" /> Processing Batch...</span>) : ("⚡ Execute Agent (Batch 5)")}
                  </button>
                </div>

                {logs.length > 0 && (
                  <div className="terminal-window">
                    <div className="terminal-header">
                      <div className="terminal-dots"><span className="dot red"></span><span className="dot yellow"></span><span className="dot green"></span></div>
                      <span className="terminal-title">agent_log.txt</span>
                    </div>
                    <div className="terminal-body">
                      {logs.map((log, i) => (
                        <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="log-line">
                          <span className="prompt">{'>'}</span> {log}
                        </motion.div>
                      ))}
                      <div className="typing-cursor">_</div>
                    </div>
                  </div>
                )}
                
                <button onClick={logout} className="btn-secondary"><LogOut size={14} /> Disconnect System</button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}

export default App;