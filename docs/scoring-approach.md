# Scoring Approach

This project uses a hybrid scoring pipeline:

- a deterministic local scoring engine for consistent behavior
- optional Gemini-assisted comparison when the API key is configured

## Score Weights

The final score is a weighted sum of four components:

- Skills Match = 40%
- Experience Match = 30%
- Education Match = 10%
- Semantic Similarity = 20%

Formula:

```text
final_score = (skills_score * 0.4)
            + (experience_score * 0.3)
            + (education_score * 0.1)
            + (semantic_score * 0.2)
```

## Component Breakdown

### Skills Score
- Compares extracted resume skills against extracted job description skills.
- When Gemini is available, the Gemini match score can replace the local skills score.
- When Gemini is unavailable or fails, the local score is used.

### Experience Score
- Extracts years of experience from resume and JD text.
- Uses a local deterministic rule so different resumes produce different values even without Gemini.

### Education Score
- Compares resume education against required education in the job description.
- If the JD does not specify education, the score still uses resume content rather than falling back to a fixed constant.

### Semantic Score
- Uses token overlap plus a cosine-style token-frequency comparison.
- This prevents a constant or fixed similarity value across all candidates.

## Gemini Behavior

Gemini is used only as an enhancement, not as a hard dependency.

- If Gemini returns valid JSON, the backend uses its comparison output.
- If Gemini is missing, fails, or returns invalid data, the backend falls back to deterministic local scoring.
- The fallback path does not return a hardcoded score.

## Output Fields

The API returns a score breakdown like this:

```json
{
  "skills_score": 35,
  "experience_score": 20,
  "education_score": 10,
  "semantic_score": 18,
  "final_score": 83
}
```

## Logging

The scoring service logs each component for traceability:

- `Skills Score`
- `Experience Score`
- `Education Score`
- `Semantic Score`
- `Final Score`

This helps debug cases where scores appear too similar or unexpectedly flat.

## Regression Coverage

A scoring regression test verifies that:

- a strong resume scores higher than a medium resume
- a medium resume scores higher than a poor resume
- score differences are significant enough to avoid identical rankings
