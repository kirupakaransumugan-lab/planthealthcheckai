import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function Login() {

    const { user, login } = useAuth();
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);


    // Already logged in: nothing to do here
    if (user) {
        return <Navigate to="/" replace />;
    }


    async function handleSubmit(event) {

        event.preventDefault();
        setError("");

        if (!email.trim() || !password) {
            setError("Please enter your email and password.");
            return;
        }

        try {
            setLoading(true);
            await login(email.trim(), password);
            navigate("/");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }


    return (
        <div className="auth-wrap">
            <form className="card auth-card" onSubmit={handleSubmit}>

                <h2>Welcome back</h2>
                <p className="sub">Log in to analyze plants and see your history.</p>

                <label className="field">
                    <span>Email</span>
                    <input
                        type="email"
                        autoComplete="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </label>

                <label className="field">
                    <span>Password</span>
                    <input
                        type="password"
                        autoComplete="current-password"
                        placeholder="Your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </label>

                {error && (
                    <p className="alert" role="alert">{error}</p>
                )}

                <button className="btn" type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Log in"}
                </button>

                <p className="auth-switch">
                    New here? <Link to="/register">Create an account</Link>
                </p>

            </form>
        </div>
    );
}


export default Login;
