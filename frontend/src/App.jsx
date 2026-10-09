import { Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar";
import { useAuth } from "./context/AuthContext";
import HistoryPage from "./pages/HistoryPage";
import Home from "./pages/Home";
import Login from "./pages/Login";
import PeoplePage from "./pages/PeoplePage";
import Register from "./pages/Register";


function App() {

    const { ready } = useAuth();


    return (
        <div className="page">

            <Navbar />

            <main className="container">
                {/* Wait until we know if the saved login is still valid */}
                {ready ? (
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/history" element={<HistoryPage />} />
                        <Route path="/people" element={<PeoplePage />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="*" element={<Home />} />
                    </Routes>
                ) : (
                    <p className="muted-text">Loading...</p>
                )}
            </main>

            <footer className="footer">
                AI-generated suggestions are for educational purposes only
                and are not a guaranteed diagnosis.
            </footer>

        </div>
    );
}


export default App;
