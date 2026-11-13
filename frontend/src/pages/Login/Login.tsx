
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, GraduationCap, Lock, Mail } from "lucide-react";

import { useAuth } from "../../context/AuthContext";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");

    if (!username.trim() || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setIsLoading(true);

      await login(username.trim(), password);

      navigate("/dashboard", { replace: true });
    } catch {
      setError("Invalid email or password. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-left">
        <div className="login-brand">
          <div className="brand-icon">
            <GraduationCap size={30} />
          </div>

          <div>
            <h2>School Intelligence</h2>
            <span>Academic Analytics Platform</span>
          </div>
        </div>

        <div className="login-content">
          <span className="welcome-label">WELCOME BACK</span>

          <h1>
            Smarter Insights.
            <br />
            Better Education.
          </h1>

          <p>
            Transform academic data into meaningful insights.
            Monitor student performance, track attendance,
            and make data-driven educational decisions.
          </p>

          <div className="login-features">
            <div>
              <span className="feature-dot" />
              Academic Performance Analytics
            </div>

            <div>
              <span className="feature-dot" />
              AI-Powered Academic Assistant
            </div>

            <div>
              <span className="feature-dot" />
              Predictive Student Intelligence
            </div>
          </div>
        </div>

        <div className="login-footer">
          © 2026 School Intelligence. All rights reserved.
        </div>
      </div>

      <div className="login-right">
        <div className="login-card">
          <div className="login-heading">
            <h1>Sign in</h1>
            <p>Enter your credentials to access your account.</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">Email Address</label>

              <div className="input-wrapper">
                <Mail size={19} />

                <input
                  id="username"
                  type="email"
                  placeholder="Enter your email address"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  autoComplete="username"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>

              <div className="input-wrapper">
                <Lock size={19} />

                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                  disabled={isLoading}
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff size={19} />
                  ) : (
                    <Eye size={19} />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="login-button"
              disabled={isLoading}
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="login-security">
            <Lock size={15} />
            <span>Secure access to your academic intelligence platform</span>
          </div>
        </div>
      </div>
    </div>
  );
}
