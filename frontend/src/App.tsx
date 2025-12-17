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

  return (
    <div className="app-container" style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>📨 Inbox Zero Agent</h1>
      <p>Connect your Gmail to let the AI draft replies.</p>
      
      <div style={{ marginTop: '2rem' }}>
        {!user ? (
          <button 
            onClick={() => googleLogin()} 
            disabled={loading}
            style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
          >
            {loading ? "Verifying..." : "🚀 Connect Gmail"}
          </button>
        ) : (
          <div className="dashboard">
            <h3>✅ Welcome, {user.email}</h3>
            <p>Agent is Active. Status: <strong>Standby</strong></p>
            <button onClick={() => setUser(null)}>Logout</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;