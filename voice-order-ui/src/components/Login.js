import React, { useState } from 'react';
import { signInWithEmailAndPassword, signInAnonymously } from "firebase/auth";
import { auth } from '../firebase';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await signInWithEmailAndPassword(auth, email, password);
      console.log("Logged in successfully");
      navigate("/voice-order");
    } catch (err) {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnonymousLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      await signInAnonymously(auth);
      console.log("Logged in as guest");
      navigate("/voice-order");
    } catch (err) {
      setError("Failed to sign in anonymously.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <button onClick={handleAnonymousLogin} disabled={loading}>
        {loading ? "Logging in..." : "Login as Guest"}
      </button>
      {error && <p className="error">{error}</p>}
      <p className="signup-redirect">
        Don’t have an account? <a href="/signup">Sign up here</a>
      </p>
    </div>
  );
};

export default Login;
