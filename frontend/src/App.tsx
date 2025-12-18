import { useState } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import './App.css';

function App() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // 1. The Login Hook
  const googleLogin = useGoogleLogin({
    flow: 'auth-code', // <--- CRITICAL: This gives us a "Code" to swap for a Refresh Token
    scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose',
    onSuccess: async (codeResponse) => {
      console.log("Google gave us this code:", codeResponse.code);
      setLoading(true);
      
      // 2. Send the code to our Backend
      try {
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/google`, {
          code: codeResponse.code,
        });
        console.log("Backend verified user:", res.data);
        setUser(res.data.user);
      } catch (error) {
        console.error("Backend login failed:", error);
        alert("Login failed! Check console.");
      } finally {
        setLoading(false);
      }
    },
    onError: errorResponse => console.log(errorResponse),
  });

  const runAgent = async () => {
    if (!user) return;
    setLoading(true);
    try {
      // Call our new endpoint
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/run-agent`, {
        email: user.email // Send the email so backend knows which tokens to use
      });
      
      console.log("Agent finished:", res.data);
      alert(`🤖 Agent says:\n\n${res.data.agent_response}`);
    } catch (error: any) {
      console.error("Agent failed:", error);
      alert("Agent failed! Check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>📨 Inbox Zero Agent</h1>
      
      <div style={{ marginTop: '2rem' }}>
        {!user ? (
          /* Login Button (Keep your existing GoogleLogin code here) */
          <button onClick={() => googleLogin()}>🚀 Connect Gmail</button>
        ) : (
          /* Dashboard */
          <div className="dashboard">
            <h3>✅ Welcome, {user.email}</h3>
            <p>Ready to process your inbox.</p>
            
            <div style={{ margin: '20px 0' }}>
              <button 
                onClick={runAgent} 
                disabled={loading}
                style={{ 
                  padding: '15px 30px', 
                  fontSize: '18px', 
                  backgroundColor: loading ? '#ccc' : '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? "🤖 Agent Working..." : "⚡ Run Inbox Zero Agent"}
              </button>
            </div>
            
            <button onClick={() => setUser(null)} style={{marginTop: '20px'}}>Logout</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;