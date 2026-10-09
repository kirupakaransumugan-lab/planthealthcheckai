import { createContext, useCallback, useContext, useEffect, useState } from "react";

import {
    clearToken,
    getCurrentUser,
    getToken,
    loginUser,
    registerUser,
    setToken,
    setUnauthorizedHandler
} from "../services/api";


const AuthContext = createContext(null);


export function AuthProvider({ children }) {

    const [user, setUser] = useState(null);

    // False until we know whether the saved token is still valid
    const [ready, setReady] = useState(false);


    const logout = useCallback(() => {
        clearToken();
        setUser(null);
    }, []);


    // On first load, check the saved token with the backend
    useEffect(() => {

        setUnauthorizedHandler(logout);

        if (!getToken()) {
            setReady(true);
            return;
        }

        getCurrentUser()
            .then(setUser)
            .catch(() => clearToken())
            .finally(() => setReady(true));
    }, [logout]);


    async function login(email, password) {

        const data = await loginUser(email, password);

        setToken(data.token);
        setUser(data.user);
    }


    async function register(name, email, password) {

        const data = await registerUser(name, email, password);

        setToken(data.token);
        setUser(data.user);
    }


    return (
        <AuthContext.Provider value={{ user, ready, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
}


export function useAuth() {
    return useContext(AuthContext);
}
