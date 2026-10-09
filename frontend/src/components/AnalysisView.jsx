// Shows one structured analysis (used for new results and for history items)
function AnalysisView({ analysis }) {

    return (
        <div className="analysis">

            <h3>Possible issues</h3>
            <ul>
                {analysis.possible_issues.map((issue, index) => (
                    <li key={index}>{issue}</li>
                ))}
            </ul>


            <h3>Explanation</h3>
            <p>{analysis.explanation}</p>


            <h3>Care suggestions</h3>
            <ol>
                {analysis.care_suggestions.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                ))}
            </ol>


            <h3>When to ask an expert</h3>
            <p>{analysis.expert_advice}</p>


            <p className="confidence-note">{analysis.confidence_note}</p>

        </div>
    );
}


export default AnalysisView;
