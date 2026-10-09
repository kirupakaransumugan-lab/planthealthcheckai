import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { analyzePlant, getPeople } from "../services/api";
import AnalysisView from "./AnalysisView";


const LAST_PERSON_KEY = "plantcare_last_person";


function PlantForm() {

    const [formData, setFormData] = useState({
        plant_name: "",
        plant_type: "",
        location: "",
        symptom: ""
    });

    const [people, setPeople] = useState([]);
    const [personId, setPersonId] = useState("");

    const [error, setError] = useState("");
    const [analysis, setAnalysis] = useState(null);
    const [saved, setSaved] = useState(false);
    const [loading, setLoading] = useState(false);


    // Load the people this account can check plants for
    useEffect(() => {

        getPeople()
            .then((list) => {
                setPeople(list);

                // Pre-select the person used last time, otherwise the first one
                let lastId = null;

                try {
                    lastId = Number(localStorage.getItem(LAST_PERSON_KEY));
                } catch (err) {
                    // Storage blocked; fall back to the first person
                }

                const remembered = list.find((p) => p.id === lastId);

                setPersonId(String(remembered ? remembered.id : list[0]?.id ?? ""));
            })
            .catch((err) => setError(err.message));
    }, []);


    function handlePersonChange(event) {

        setPersonId(event.target.value);

        try {
            localStorage.setItem(LAST_PERSON_KEY, event.target.value);
        } catch (err) {
            // Not important if it cannot be remembered
        }
    }


    function handleChange(event) {

        const { name, value } = event.target;

        setFormData({
            ...formData,
            [name]: value
        });
    }


    async function handleSubmit(event) {

        event.preventDefault();

        setError("");
        setAnalysis(null);


        if (!personId) {
            setError("Please choose who this plant check is for.");
            return;
        }


        if (!formData.plant_name.trim()) {
            setError("Please enter the plant name.");
            return;
        }


        if (!formData.plant_type.trim()) {
            setError("Please enter the plant type.");
            return;
        }


        if (formData.symptom.trim().length < 5) {
            setError("Please describe the symptoms (at least 5 characters).");
            return;
        }


        try {

            setLoading(true);

            const data = await analyzePlant({
                person_id: Number(personId),
                plant_name: formData.plant_name.trim(),
                plant_type: formData.plant_type.trim(),
                location: formData.location.trim() || null,
                symptom: formData.symptom.trim()
            });

            setAnalysis(data.analysis);
            setSaved(data.saved);

        } catch (err) {

            setError(err.message);

        } finally {

            setLoading(false);
        }
    }


    return (
        <>
                <div className="grid">

                    {/* ---------- Form ---------- */}
                    <form className="card" onSubmit={handleSubmit}>

                        <h2>Describe your plant</h2>
                        <p className="sub">
                            The more detail you give, the more useful the analysis.
                        </p>

                        <label className="field">
                            <span>Who is this plant check for?</span>
                            <select
                                value={personId}
                                onChange={handlePersonChange}
                            >
                                {people.map((person) => (
                                    <option key={person.id} value={person.id}>
                                        {person.name}
                                        {person.location ? ` (${person.location})` : ""}
                                    </option>
                                ))}
                            </select>
                            <small className="field-hint">
                                Need someone new? <Link to="/people">Add a person</Link>
                            </small>
                        </label>

                        <label className="field">
                            <span>Plant name</span>
                            <input
                                type="text"
                                name="plant_name"
                                placeholder="e.g. Tomato"
                                value={formData.plant_name}
                                onChange={handleChange}
                            />
                        </label>

                        <label className="field">
                            <span>Plant type</span>
                            <input
                                type="text"
                                name="plant_type"
                                placeholder="e.g. Vegetable, houseplant, fruit tree"
                                value={formData.plant_type}
                                onChange={handleChange}
                            />
                        </label>

                        <label className="field">
                            <span>Location <em>(optional)</em></span>
                            <input
                                type="text"
                                name="location"
                                placeholder="e.g. Balcony, garden, indoors by a window"
                                value={formData.location}
                                onChange={handleChange}
                            />
                        </label>

                        <label className="field">
                            <span>Symptoms</span>
                            <textarea
                                name="symptom"
                                placeholder="e.g. Lower leaves turning yellow with brown spots for a week..."
                                value={formData.symptom}
                                onChange={handleChange}
                            />
                        </label>


                        {error && (
                            <p className="alert" role="alert">{error}</p>
                        )}


                        <button
                            className="btn"
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Analyzing..."
                                : "Analyze Plant"
                            }
                        </button>

                    </form>


                    {/* ---------- Result ---------- */}
                    <section className="card" aria-live="polite">

                        {loading && (
                            <div className="loading">
                                <div className="spinner" />
                                <strong>Analyzing plant health...</strong>
                                <span>
                                    Please wait while the AI evaluates the symptoms.
                                </span>
                            </div>
                        )}


                        {!loading && !analysis && (
                            <div className="placeholder">
                                <div className="big">🌱</div>
                                <h2>Your analysis will appear here</h2>
                                <ul>
                                    <li>Possible causes of the problem</li>
                                    <li>Three simple care suggestions</li>
                                    <li>When to ask an agricultural expert</li>
                                </ul>
                            </div>
                        )}


                        {analysis && !loading && (
                            <>
                                <div className="result-head">
                                    <h2>Plant Health Analysis</h2>
                                    <span className="badge">AI-generated</span>
                                </div>

                                <AnalysisView analysis={analysis} />

                                <p className="saved-note">
                                    {saved ? (
                                        <>Saved to your history. <Link to="/history">View history</Link></>
                                    ) : (
                                        <>This result could not be saved to your history.</>
                                    )}
                                </p>

                                <p className="disclaimer">
                                    This is an educational suggestion, not a
                                    guaranteed diagnosis. If the problem continues
                                    or spreads, consult a local agricultural expert.
                                </p>
                            </>
                        )}

                    </section>

                </div>
        </>
    );
}


export default PlantForm;
