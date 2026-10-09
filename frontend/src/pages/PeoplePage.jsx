import { useCallback, useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import {
    createPerson,
    deletePerson,
    getPeople,
    updatePerson
} from "../services/api";


const EMPTY_FORM = { name: "", location: "", notes: "" };


function PeoplePage() {

    const { user } = useAuth();

    const [people, setPeople] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [form, setForm] = useState(EMPTY_FORM);
    const [saving, setSaving] = useState(false);

    // Which person is being edited (null = none) and the edit form values
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState(EMPTY_FORM);


    const loadPeople = useCallback(async () => {

        try {
            setError("");
            setPeople(await getPeople());
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);


    useEffect(() => {
        if (user) {
            loadPeople();
        }
    }, [user, loadPeople]);


    if (!user) {
        return <Navigate to="/login" replace />;
    }


    function toPayload(values) {
        return {
            name: values.name.trim(),
            location: values.location.trim() || null,
            notes: values.notes.trim() || null
        };
    }


    async function handleAdd(event) {

        event.preventDefault();
        setError("");

        if (!form.name.trim()) {
            setError("Please enter the person's name.");
            return;
        }

        try {
            setSaving(true);
            await createPerson(toPayload(form));
            setForm(EMPTY_FORM);
            await loadPeople();
        } catch (err) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    }


    function startEdit(person) {
        setEditingId(person.id);
        setEditForm({
            name: person.name,
            location: person.location || "",
            notes: person.notes || ""
        });
    }


    async function handleSaveEdit(event) {

        event.preventDefault();
        setError("");

        if (!editForm.name.trim()) {
            setError("The name cannot be empty.");
            return;
        }

        try {
            await updatePerson(editingId, toPayload(editForm));
            setEditingId(null);
            await loadPeople();
        } catch (err) {
            setError(err.message);
        }
    }


    async function handleDelete(person) {

        const warning = person.analysis_count > 0
            ? `Delete ${person.name} and their ${person.analysis_count} saved check(s)? This cannot be undone.`
            : `Delete ${person.name}?`;

        if (!window.confirm(warning)) {
            return;
        }

        try {
            setError("");
            await deletePerson(person.id);
            await loadPeople();
        } catch (err) {
            setError(err.message);
        }
    }


    return (
        <>
            <header className="hero">
                <h1>Your <span>People</span></h1>
                <p>Add the people you check plants for. Each person keeps their own history.</p>
            </header>


            <div className="grid">

                <form className="card" onSubmit={handleAdd}>

                    <h2>Add a person</h2>
                    <p className="sub">
                        Then choose them when you describe a plant issue.
                    </p>

                    <label className="field">
                        <span>Name</span>
                        <input
                            type="text"
                            placeholder="e.g. Ravi"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                        />
                    </label>

                    <label className="field">
                        <span>Location <em>(optional)</em></span>
                        <input
                            type="text"
                            placeholder="e.g. Jaffna"
                            value={form.location}
                            onChange={(e) => setForm({ ...form, location: e.target.value })}
                        />
                    </label>

                    <label className="field">
                        <span>Notes <em>(optional)</em></span>
                        <input
                            type="text"
                            placeholder="e.g. Grows onions and chillies"
                            value={form.notes}
                            onChange={(e) => setForm({ ...form, notes: e.target.value })}
                        />
                    </label>

                    {error && (
                        <p className="alert" role="alert">{error}</p>
                    )}

                    <button className="btn" type="submit" disabled={saving}>
                        {saving ? "Adding..." : "Add person"}
                    </button>

                </form>


                <section className="card">

                    <h2>People ({people.length})</h2>
                    <p className="sub">Select one of them on the Home page to check a plant.</p>

                    {loading && <p className="muted-text">Loading...</p>}

                    <div className="history-list">
                        {people.map((person) => (
                            <div className="person-row" key={person.id}>

                                {editingId === person.id ? (
                                    <form className="person-edit" onSubmit={handleSaveEdit}>
                                        <input
                                            type="text"
                                            value={editForm.name}
                                            placeholder="Name"
                                            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                                        />
                                        <input
                                            type="text"
                                            value={editForm.location}
                                            placeholder="Location"
                                            onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                                        />
                                        <input
                                            type="text"
                                            value={editForm.notes}
                                            placeholder="Notes"
                                            onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
                                        />
                                        <div className="person-actions">
                                            <button type="submit" className="btn-small save">Save</button>
                                            <button
                                                type="button"
                                                className="btn-small"
                                                onClick={() => setEditingId(null)}
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </form>
                                ) : (
                                    <>
                                        <div className="person-info">
                                            <strong>{person.name}</strong>
                                            <span className="history-meta">
                                                {person.location ? `${person.location} · ` : ""}
                                                {person.analysis_count} saved check{person.analysis_count === 1 ? "" : "s"}
                                            </span>
                                            {person.notes && (
                                                <span className="history-meta">{person.notes}</span>
                                            )}
                                        </div>

                                        <div className="person-actions">
                                            <Link className="btn-small save" to={`/history?person=${person.id}`}>
                                                History
                                            </Link>
                                            <button
                                                type="button"
                                                className="btn-small"
                                                onClick={() => startEdit(person)}
                                            >
                                                Edit
                                            </button>
                                            <button
                                                type="button"
                                                className="btn-small danger"
                                                onClick={() => handleDelete(person)}
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </>
                                )}

                            </div>
                        ))}
                    </div>

                </section>

            </div>
        </>
    );
}


export default PeoplePage;
