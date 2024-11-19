import React, { useState, useEffect } from 'react';
import { signInWithEmailAndPassword, signInAnonymously, onAuthStateChanged } from "firebase/auth";
import { auth } from '../firebase';
import { useNavigate, Link } from 'react-router-dom';
import innsightLogo from '../components/innsight_logo_png.png';

// IMPORTS BY CHRIS
import 'bootstrap/dist/css/bootstrap.min.css';
import './Login.css';
import FloatingLabel from "react-bootstrap/FloatingLabel";
import Form from "react-bootstrap/Form";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        navigate("/voice-order");
      }
    });

    return () => unsubscribe();
  }, [navigate]);

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
    <div className="login-page">
      <div className="login-container">
        <img src={innsightLogo} alt="logo" />
        <h2><b>INNSIGHT</b></h2>
        <form onSubmit={handleLogin} className="w-100">
          <FloatingLabel
            controlId="floatingEmail"
            label="Email Address"
            className="mb-3 w-100"
          >
            <Form.Control
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-100"
            />
          </FloatingLabel>

          <FloatingLabel
            controlId="floatingPassword"
            label="Password"
            className="mb-3 w-100"
          >
            <Form.Control
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-100"
            />
          </FloatingLabel>

          <button type="submit" className="btn btn-primary w-100" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <button
          onClick={handleAnonymousLogin}
          className="btn btn-secondary w-100 mt-2"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login as Guest"}
        </button>

        {error && <p className="error text-danger mt-2">{error}</p>}

        <p className="signup-redirect mt-3">
          Don’t have an account? <Link to="/signup" className="custom-link">Sign up here</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
