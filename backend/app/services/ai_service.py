import logging
import time

try:
    from google import genai  # type: ignore[import-not-found]
    from google.genai import errors, types  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - dependency may be missing in local tooling
    genai = None
    errors = None
    types = None

from app.config import GEMINI_API_KEY, GEMINI_MODELS
from app.schemas.plant import PlantAnalysisResult

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3

if genai is None or errors is None or types is None:
    raise RuntimeError("The 'google-genai' package is required for AI analysis.")


# 30s timeout (milliseconds) so a slow response can't hang the UI forever
client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(timeout=30000)
)


def analyze_plant(
    plant_name: str,
    plant_type: str,
    location: str | None,
    symptom: str
) -> tuple[PlantAnalysisResult, str]:
    """Returns (structured result, name of the model that produced it)."""

    location_text = location if location else "Not provided"

    prompt = f"""
You are an educational plant-care assistant.

Analyze the following plant information:

Plant name: {plant_name}
Plant type: {plant_type}
Location: {location_text}
Symptoms: {symptom}

Fill in the requested fields with a short educational plant health analysis.
Provide exactly three care suggestions.

Important instructions:

- Do not claim that you have made a guaranteed diagnosis.
- Clearly explain that the possible issues are not certain.
- Consider multiple possible causes when appropriate.
- Give practical and simple advice.
- Do not recommend dangerous chemical treatments.
- Keep the response easy for a home gardener or farmer to understand.
"""

    # Ask Gemini for JSON that matches PlantAnalysisResult
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=PlantAnalysisResult
    )

    last_error = None

    # Try each model in order. Free-tier quota is counted per model, so when
    # one is out of quota (429) or retired (404) the next one can still answer.
    for model in GEMINI_MODELS:

        # Retry a few times: Gemini returns 503 during temporary demand spikes
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config
                )

                result = response.parsed

                if not isinstance(result, PlantAnalysisResult):
                    result = PlantAnalysisResult.model_validate_json(response.text)

                return result, model

            except errors.ServerError as e:
                last_error = e

                if attempt < MAX_ATTEMPTS:
                    time.sleep(2 * attempt)

            except errors.ClientError as e:
                last_error = e

                if e.code in (404, 429):
                    logger.warning("Model %s unavailable (%s), trying next", model, e.code)
                    break

                raise

    raise last_error
