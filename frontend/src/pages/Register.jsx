import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function Register() {

    const { user, register } = useAuth();
    const navigate = useNavigate();

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirm, setConfirm] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);


    if (user) {
        return <Navigate to="/" replace />;
    }


    async function handleSubmit(event) {

        event.preventDefault();
        setError("");

        if (!name.trim()) {
            setError("Please enter your name.");
            return;
        }

        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.trim())) {
            setError("Please enter a valid email address.");
            return;
        }

        if (password.length < 8) {
            setError("Password must be at least 8 characters long.");
            return;
        }

        if (password !== confirm) {
            setError("The two passwords do not match.");
            return;
        }

        try {
            setLoading(true);
            await register(name.trim(), email.trim(), password);
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

                <h2>Create your account</h2>
                <p className="sub">Save your plant checks and revisit them anytime.</p>

                <label className="field">
                    <span>Name</span>
                    <input
                        type="text"
                        autoComplete="name"
                        placeholder="e.g. Kumar"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                    />
                </label>

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
                    <span>Password <em>(at least 8 characters)</em></span>
                    <input
                        type="password"
                        autoComplete="new-password"
                        placeholder="Choose a password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </label>

                <label className="field">
                    <span>Confirm password</span>
                    <input
                        type="password"
                        autoComplete="new-password"
                        placeholder="Type it again"
                        value={confirm}
                        onChange={(e) => setConfirm(e.target.value)}
                    />
                </label>

                {error && (
                    <p className="alert" role="alert">{error}</p>
                )}

                <button className="btn" type="submit" disabled={loading}>
                    {loading ? "Creating account..." : "Register"}
                </button>

                <p className="auth-switch">
                    Already have an account? <Link to="/login">Log in</Link>
                </p>

            </form>
        </div>
    );
}


export default Register;
