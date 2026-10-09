import { Navigate } from "react-router-dom";

import History from "../components/History";
import { useAuth } from "../context/AuthContext";


function HistoryPage() {

    const { user } = useAuth();


    // History belongs to an account, so send visitors to the login page
    if (!user) {
        return <Navigate to="/login" replace />;
    }


    return (
        <>
            <header className="hero">
                <h1>Your <span>History</span></h1>
                <p>Every plant check you have saved, newest first.</p>
            </header>

            <History />
        </>
    );
}


export default HistoryPage;
