import { useState, useEffect } from 'react';
import ResultsTable from '@/components/ResultsTable';
import ResultsChart from '@/components/ResultsChart';

export default function Home() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [mode, setMode] = useState('login');
  const [history, setHistory] = useState([]);
  const lilac = '#C8A2C8';

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedToken = localStorage.getItem('token');
      const savedUsername = localStorage.getItem('username');
      if (savedToken) setToken(savedToken);
      if (savedUsername) setUsername(savedUsername);
    }
  }, []);

  useEffect(() => {
    if (token) {
      document.getElementById('queryInput')?.focus();
    }
  }, [token]);

  const validatePassword = (pwd) => {
    return (
      pwd.length >= 8 &&
      /[A-Z]/.test(pwd) &&
      /[^a-zA-Z0-9]/.test(pwd)
    );
  };

  const handleAuth = async () => {
    if (!validatePassword(password)) {
      setError('Password must be 8+ chars, 1 uppercase, 1 special char.');
      return;
    }

    try {
      const url = `http://localhost:5050/${mode}`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.msg || 'Auth failed');

      if (mode === 'login') {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('username', username);
        setToken(data.access_token);
      }

      setError('');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubmit = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Missing JWT token. Please login.');
      return;
    }

    try {
      const res = await fetch('http://localhost:5050/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Query failed');

      setResult(data);
      setHistory((prev) => [query, ...prev.slice(0, 4)]);
      setError('');
    } catch (err) {
      setError(err.message);
      setResult(null);
    }
  };

  return (
    <main style={{ fontFamily: 'Arial, sans-serif', background: '#fff', minHeight: '100vh' }}>
      {!token ? (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}>
          <div style={{
            border: `1px solid ${lilac}`,
            borderRadius: '10px',
            padding: '2rem',
            width: '350px',
            boxShadow: `0 4px 10px rgba(200, 162, 200, 0.2)`,
            textAlign: 'center'
          }}>
            <h2 style={{ color: lilac, fontSize: '1.5rem', marginBottom: '1rem' }}>
              {mode === 'login' ? 'Login' : 'Sign Up'}
            </h2>
            <div style={{ marginBottom: '1rem' }}>
              <button
                onClick={() => setMode('login')}
                disabled={mode === 'login'}
                style={{ marginRight: '1rem', color: lilac, background: 'transparent', border: 'none', cursor: 'pointer' }}
              >
                Login
              </button>
              <button
                onClick={() => setMode('signup')}
                disabled={mode === 'signup'}
                style={{ color: lilac, background: 'transparent', border: 'none', cursor: 'pointer' }}
              >
                Sign Up
              </button>
            </div>
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem', borderRadius: '5px', border: `1px solid ${lilac}` }}
            />
            <input
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem', borderRadius: '5px', border: `1px solid ${lilac}` }}
            />
            <button
              onClick={handleAuth}
              style={{ backgroundColor: lilac, color: '#fff', padding: '0.5rem 1rem', borderRadius: '5px', border: 'none', width: '100%' }}
            >
              {mode === 'login' ? 'Login' : 'Sign Up'}
            </button>
            {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
          </div>
        </div>
      ) : (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
          <h1 style={{ color: lilac, textAlign: 'center', marginBottom: '1rem' }}>
            FHIR Natural Language Health Query Tool
          </h1>
          <p style={{ color: lilac, textAlign: 'center', marginBottom: '2rem' }}>
            Welcome, <strong>{username}</strong>!
          </p>

          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            marginBottom: '2rem',
          }}>
            <input
              id="queryInput"
              type="text"
              placeholder="Enter query (e.g., patients with asthma)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{
                padding: '0.5rem',
                borderRadius: '5px 0 0 5px',
                border: `1px solid ${lilac}`,
                flexGrow: 1
              }}
            />
            <button
              onClick={handleSubmit}
              style={{
                backgroundColor: lilac,
                color: '#fff',
                padding: '0.5rem 1rem',
                borderRadius: '0 5px 5px 0',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              🔍
            </button>
            <button
              onClick={() => {
                localStorage.removeItem('token');
                localStorage.removeItem('username');
                setToken('');
                setResult(null);
                setError('');
              }}
              style={{
                marginLeft: '1rem',
                backgroundColor: 'gray',
                color: '#fff',
                padding: '0.5rem 1rem',
                borderRadius: '5px',
                border: 'none'
              }}
            >
              Logout
            </button>
          </div>

          {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

          {result?.entry?.length === 0 && (
            <p style={{ color: 'gray', textAlign: 'center' }}>
              No results found for your query.
            </p>
          )}

          {result?.entry?.length > 0 && (
            <div>
              <h2 style={{ color: lilac, marginBottom: '1rem' }}>FHIR Simulated Output</h2>
              <ResultsTable data={result?.entry?.map((e) => e.resource)} />
              <h3 style={{ color: lilac, marginTop: '2rem' }}>Conditions Chart</h3>
              <ResultsChart data={result?.entry?.map((e) => e.resource)} />
            </div>
          )}

          {history.length > 0 && (
            <div style={{ marginTop: '2rem' }}>
              <h3 style={{ color: lilac }}>Recent Queries</h3>
              <ul>
                {history.map((q, i) => (
                  <li key={i} style={{ color: 'gray' }}>{q}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
