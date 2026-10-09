const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
const TOKEN_KEY = "plantcare_token";


// ---------- Login token (kept in this browser) ----------

export function getToken() {

    try {
        return localStorage.getItem(TOKEN_KEY);
    } catch (err) {
        return null;
    }
}


export function setToken(token) {

    try {
        localStorage.setItem(TOKEN_KEY, token);
    } catch (err) {
        // Storage can be blocked (private mode); the login lasts until the tab closes
    }
}


export function clearToken() {

    try {
        localStorage.removeItem(TOKEN_KEY);
    } catch (err) {
        // Nothing to clean up
    }
}


// AuthContext registers a function here so an expired login logs the user out
let onUnauthorized = null;

export function setUnauthorizedHandler(handler) {
    onUnauthorized = handler;
}


// ---------- Shared request helper ----------

export class ApiError extends Error {

    constructor(message, status) {
        super(message);
        this.status = status;
    }
}


// Turns the backend's error body into one readable sentence
async function readErrorMessage(response) {

    try {
        const body = await response.json();

        if (typeof body.detail === "string") {
            return body.detail;
        }

        // Validation errors (422) arrive as a list; show the first one
        if (Array.isArray(body.detail) && body.detail.length > 0) {
            return body.detail[0].msg.replace(/^Value error, /, "");
        }
    } catch (err) {
        // Response was not JSON
    }

    return "Something went wrong. Please try again.";
}


async function request(path, { method = "GET", body, auth = true } = {}) {

    const headers = {};

    if (body !== undefined) {
        headers["Content-Type"] = "application/json";
    }

    const token = getToken();

    if (auth && token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    let response;

    try {
        response = await fetch(`${API_URL}${path}`, {
            method,
            headers,
            body: body !== undefined ? JSON.stringify(body) : undefined
        });
    } catch (err) {
        throw new ApiError(
            "Cannot reach the server. Is the backend running?",
            0
        );
    }

    if (!response.ok) {

        // A 401 on a protected call means the login expired
        if (response.status === 401 && auth && onUnauthorized) {
            onUnauthorized();
        }

        throw new ApiError(await readErrorMessage(response), response.status);
    }

    return response.json();
}


// ---------- Authentication ----------

export function registerUser(name, email, password) {
    return request("/auth/register", {
        method: "POST",
        body: { name, email, password },
        auth: false
    });
}


export function loginUser(email, password) {
    return request("/auth/login", {
        method: "POST",
        body: { email, password },
        auth: false
    });
}


export async function getCurrentUser() {

    const data = await request("/auth/me");

    return data.user;
}


// ---------- Plant analysis and history ----------

export function analyzePlant(data) {
    return request("/plant/analyze", { method: "POST", body: data });
}


export async function getHistory(personId) {

    const query = personId ? `?person_id=${personId}` : "";

    const data = await request(`/plant/history${query}`);

    return data.history;
}


export function deleteHistoryItem(id) {
    return request(`/plant/history/${id}`, { method: "DELETE" });
}


export function clearHistory(personId) {

    const query = personId ? `?person_id=${personId}` : "";

    return request(`/plant/history${query}`, { method: "DELETE" });
}


// ---------- People (who the plant checks are for) ----------

export async function getPeople() {

    const data = await request("/people");

    return data.people;
}


export async function createPerson(person) {

    const data = await request("/people", { method: "POST", body: person });

    return data.person;
}


export async function updatePerson(id, person) {

    const data = await request(`/people/${id}`, { method: "PUT", body: person });

    return data.person;
}


export function deletePerson(id) {
    return request(`/people/${id}`, { method: "DELETE" });
}
