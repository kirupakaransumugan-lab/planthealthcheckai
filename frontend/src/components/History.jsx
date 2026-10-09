import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { clearHistory, deleteHistoryItem, getHistory, getPeople } from "../services/api";
import AnalysisView from "./AnalysisView";


function formatDate(isoString) {

    return new Date(isoString).toLocaleString([], {
        dateStyle: "medium",
        timeStyle: "short"
    });
}


function History() {

    // ?person=3 in the address selects one person (used by the People page links)
    const [searchParams, setSearchParams] = useSearchParams();
    const personId = searchParams.get("person") || "";

    const [people, setPeople] = useState([]);

    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");


    const loadHistory = useCallback(async () => {

        try {
            setLoading(true);
            setError("");
            setItems(await getHistory(personId));
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [personId]);


    useEffect(() => {
        getPeople().then(setPeople).catch(() => {});
    }, []);


    useEffect(() => {
        loadHistory();
    }, [loadHistory]);


    async function handleDelete(id) {

        try {
            await deleteHistoryItem(id);
            setItems((current) => current.filter((item) => item.id !== id));
        } catch (err) {
            setError(err.message);
        }
    }


    async function handleClear() {

        const who = people.find((p) => String(p.id) === personId);

        if (!window.confirm(who ? `Delete all saved analyses for ${who.name}?` : "Delete all saved analyses?")) {
            return;
        }

        try {
            await clearHistory(personId);
            setItems([]);
        } catch (err) {
            setError(err.message);
        }
    }


    return (
        <section className="card history">

            <div className="history-head">
                <div>
                    <h2>Analysis History</h2>
                    <p className="sub">
                        Previous plant checks, newest first.
                    </p>
                </div>

                <label className="history-filter">
                    <span>Show</span>
                    <select
                        value={personId}
                        onChange={(e) =>
                            setSearchParams(e.target.value ? { person: e.target.value } : {})
                        }
                    >
                        <option value="">Everyone</option>
                        {people.map((person) => (
                            <option key={person.id} value={person.id}>
                                {person.name}
                            </option>
                        ))}
                    </select>
                </label>

                {items.length > 0 && (
                    <button
                        type="button"
                        className="btn-small danger"
                        onClick={handleClear}
                    >
                        Clear all
                    </button>
                )}
            </div>


            {error && (
                <p className="alert" role="alert">{error}</p>
            )}


            {loading && (
                <p className="muted-text">Loading history...</p>
            )}


            {!loading && !error && items.length === 0 && (
                <div className="placeholder">
                    <div className="big">🗂️</div>
                    <p>No analyses yet. Your results will be saved here.</p>
                </div>
            )}


            <div className="history-list">
                {items.map((item) => (
                    <details className="history-item" key={item.id}>

                        <summary>
                            <div className="history-title">
                                <strong>{item.plant_name}</strong>
                                <span className="tag person-tag">👤 {item.person_name}</span>
                                <span className="tag">{item.plant_type}</span>
                            </div>

                            <div className="history-meta">
                                {formatDate(item.created_at)}
                                {item.location ? ` · ${item.location}` : ""}
                            </div>
                        </summary>

                        <div className="history-body">

                            {item.symptom && (
                                <p>
                                    <strong>Symptoms:</strong> {item.symptom}
                                </p>
                            )}

                            <AnalysisView analysis={item.analysis} />

                            <button
                                type="button"
                                className="btn-small danger"
                                onClick={() => handleDelete(item.id)}
                            >
                                Delete
                            </button>

                        </div>

                    </details>
                ))}
            </div>

        </section>
    );
}


export default History;
