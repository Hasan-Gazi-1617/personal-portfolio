"""Optional AI scoring for IELTS-style writing and speaking transcript responses.

Configure IELTS_AI_API_KEY in the hosting environment to enable provider scoring.
Without the secret, subjective responses are queued for teacher review and are
never presented as AI-graded.
"""
import json
import os
import urllib.request


def score_subjective(skill, prompt, response):
    api_key = os.environ.get("IELTS_AI_API_KEY", "").strip()
    if not api_key or not response.strip():
        return None, "AI scoring is not configured. Your response has been saved for teacher review."

    model = os.environ.get("IELTS_AI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": (
                "You are an IELTS practice assessor. Assess original practice responses, "
                "not official exam results. Return JSON only with band_score (0 to 9, "
                "one decimal), strengths (array of strings), improvements (array of strings), "
                "and concise_feedback (string). For writing, consider task response, "
                "coherence, lexical resource, and grammar. For speaking transcripts, "
                "consider fluency/coherence, vocabulary, grammar and transcript limitations. "
                "Do not claim to assess pronunciation from plain text. State that this is "
                "practice feedback, not an official IELTS band score."
            )},
            {"role": "user", "content": json.dumps({
                "skill": skill, "practice_prompt": prompt, "student_response": response
            }, ensure_ascii=False)},
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as result:
            body = json.loads(result.read().decode("utf-8"))
        parsed = json.loads(body["choices"][0]["message"]["content"])
        score = max(0, min(9, float(parsed.get("band_score", 0))))
        feedback = json.dumps({
            "strengths": parsed.get("strengths", []),
            "improvements": parsed.get("improvements", []),
            "feedback": parsed.get("concise_feedback", ""),
            "notice": "Practice estimate only. Not an official IELTS score.",
        }, ensure_ascii=False)
        return score, feedback
    except Exception:
        return None, "AI assessment could not be completed. Your response is saved for teacher review."
