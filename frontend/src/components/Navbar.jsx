import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function linkClass({ isActive }) {
    return isActive ? "nav-link active" : "nav-link";
}


function Navbar() {

    const { user, logout } = useAuth();
    const navigate = useNavigate();


    function handleLogout() {
        logout();
        navigate("/");
    }


    return (
        <nav className="navbar">
            <div className="nav-inner">

                <Link className="brand" to="/">
                    <span className="logo">🌿</span>
                    <span>PlantCare AI</span>
                </Link>

                <ul className="nav-links">
                    <li>
                        <NavLink className={linkClass} to="/" end>
                            Home
                        </NavLink>
                    </li>

                    {user ? (
                        <>
                            <li>
                                <NavLink className={linkClass} to="/people">
                                    People
                                </NavLink>
                            </li>
                            <li>
                                <NavLink className={linkClass} to="/history">
                                    History
                                </NavLink>
                            </li>
                            <li className="nav-user">Hi, {user.name}</li>
                            <li>
                                <button
                                    type="button"
                                    className="nav-link nav-button"
                                    onClick={handleLogout}
                                >
                                    Log out
                                </button>
                            </li>
                        </>
                    ) : (
                        <>
                            <li>
                                <NavLink className={linkClass} to="/login">
                                    Log in
                                </NavLink>
                            </li>
                            <li>
                                <NavLink className={linkClass} to="/register">
                                    Register
                                </NavLink>
                            </li>
                        </>
                    )}
                </ul>

            </div>
        </nav>
    );
}


export default Navbar;
