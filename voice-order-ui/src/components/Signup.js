import React, { useState } from 'react';
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from '../firebase';
import { useNavigate, Link } from 'react-router-dom';

// IMPORTS BY CHRIS
import 'bootstrap/dist/css/bootstrap.min.css';
import './Signup.css';
import FloatingLabel from "react-bootstrap/FloatingLabel";
import Form from "react-bootstrap/Form";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      await createUserWithEmailAndPassword(auth, email, password);
      console.log("Account created successfully");
      navigate("/login");
    } catch (err) {
      setError("Failed to create account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-container">
        <h2><b>Sign Up</b></h2>
        <form onSubmit={handleSignup} className="w-100">
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

          <FloatingLabel
            controlId="floatingConfirmPassword"
            label="ConfirmPassword"
            className="mb-3 w-100"
          >
            <Form.Control
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-100"
            />
          </FloatingLabel>

          <button type="submit" className="btn btn-primary w-100" disabled={loading}>
            {loading ? "Signing up..." : "Sign Up"}
          </button>
        </form>
        {error && <p className="error text-danger mt-2">{error}</p>}
        <p className="login-redirect mt-3">
          Already have an account? <Link to="/login" className="custom-link">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;
