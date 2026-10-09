import { Link } from "react-router-dom";

import PlantForm from "../components/PlantForm";
import { useAuth } from "../context/AuthContext";


function Home() {

    const { user } = useAuth();


    return (
        <>
            <header className="hero">
                <h1>Plant Health <span>Check</span></h1>
                <p>AI-powered care insights for healthier plants.</p>
            </header>


            {user ? (
                <PlantForm />
            ) : (
                <section className="card cta">
                    <div className="big">🔒</div>
                    <h2>Log in to check your plants</h2>
                    <p className="sub">
                        Create a free account to analyze plant symptoms and keep
                        a history of every check.
                    </p>

                    <div className="cta-actions">
                        <Link className="btn cta-btn" to="/login">Log in</Link>
                        <Link className="btn-outline cta-btn" to="/register">Register</Link>
                    </div>
                </section>
            )}
        </>
    );
}


export default Home;
