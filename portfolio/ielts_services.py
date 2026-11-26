"""IELTS assignment text extraction and practice assessment helpers.

Set IELTS_AI_API_KEY on the hosting service to enable AI OCR for image/scanned
PDF uploads and IELTS-style writing feedback. Scores are practice estimates.
"""
import base64
import json
import math
import os
import re
import urllib.request
from io import BytesIO


def _api_key():
    return os.environ.get("IELTS_AI_API_KEY", "").strip()


def _chat_completion(messages, model=None, json_mode=True, timeout=55):
    key = _api_key()
    if not key:
        raise RuntimeError("IELTS_AI_API_KEY is not configured.")
    payload = {
        "model": model or os.environ.get("IELTS_AI_MODEL", "gpt-4o-mini"),
        "temperature": 0.1,
        "messages": messages,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def _vision_extract(image_data, mime_type, page_label):
    encoded = base64.b64encode(image_data).decode("ascii")
    content = [
        {
            "type": "text",
            "text": (
                f"Transcribe all readable text from {page_label} exactly as written. "
                "Preserve paragraph breaks, spelling, punctuation and sentence order. "
                "Do not correct grammar, summarize, or add commentary. Return JSON "
                "with one string field named extracted_text. If no text is readable, "
                "return an empty string."
            ),
        },
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}", "detail": "high"}},
    ]
    raw = _chat_completion([{"role": "user", "content": content}], json_mode=True)
    return str(json.loads(raw).get("extracted_text", "")).strip()


def extract_uploaded_text(uploaded_file):
    """Extract text from PDF/DOCX or OCR image/scanned PDF pages with vision."""
    filename = (uploaded_file.name or "").lower()
    extension = os.path.splitext(filename)[1]
    data = uploaded_file.read()
    uploaded_file.seek(0)
    if extension == ".docx":
        from docx import Document
        document = Document(BytesIO(data))
        parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        for table in document.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text.strip() for cell in row.cells))
        text = "\n".join(parts).strip()
        if not text:
            raise ValueError("No readable text was found in this Word document.")
        return text
    if extension == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if len(text) >= 40:
            return text
        if not _api_key():
            raise ValueError("This PDF appears to be scanned. Add IELTS_AI_API_KEY to enable OCR for scanned PDFs.")
        import fitz
        document = fitz.open(stream=data, filetype="pdf")
        pages = []
        for index, page in enumerate(document[:8]):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
            pages.append(_vision_extract(pixmap.tobytes("png"), "image/png", f"PDF page {index + 1}"))
        extracted = "\n\n".join(value for value in pages if value).strip()
        if not extracted:
            raise ValueError("No readable text could be extracted from this scanned PDF.")
        return extracted
    if extension in {".png", ".jpg", ".jpeg"}:
        if not _api_key():
            raise ValueError("Image OCR requires IELTS_AI_API_KEY. You can still submit the image for teacher review.")
        mime = "image/png" if extension == ".png" else "image/jpeg"
        text = _vision_extract(data, mime, "the uploaded image")
        if not text:
            raise ValueError("No readable text was found in this image.")
        return text
    raise ValueError("Supported uploads are PDF, DOCX, PNG and JPG/JPEG files.")


def score_assignment(assignment_title, assignment_instructions, response):
    """Return IELTS Writing Task 2 criterion scores and actionable error feedback."""
    if not _api_key():
        return {
            "status": "pending",
            "notice": "AI marking is not configured yet. Your submission is saved for teacher review.",
        }
    word_count = len(re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?", response))
    system_prompt = """
You are a careful IELTS Academic Writing Task 2 practice examiner. Assess only the
student response supplied. Do not invent errors or reward memorised templates.
Return valid JSON with this exact structure:
{
  "criteria": {
    "task_response": {"score": 0.0, "feedback": "..."},
    "coherence_cohesion": {"score": 0.0, "feedback": "..."},
    "lexical_resource": {"score": 0.0, "feedback": "..."},
    "grammatical_range_accuracy": {"score": 0.0, "feedback": "..."}
  },
  "errors": [
    {"category":"Grammar|Vocabulary|Spelling|Sentence structure|Word order|Cohesion",
     "original":"exact short excerpt", "correction":"corrected version",
     "explanation":"brief reason"}
  ],
  "strengths": ["..."],
  "priority_improvements": ["..."],
  "overall_feedback": "...",
  "suggested_rewrite": "one improved example sentence, not a full essay"
}
Each criterion score must be a valid IELTS band from 0 to 9 in 0.5 increments.
Apply the official criterion meanings:
- Task Response: addresses all parts, position, relevant developed ideas/examples.
- Coherence and Cohesion: logical progression, paragraphing, referencing and linking.
- Lexical Resource: range, precision, collocation, spelling and word formation.
- Grammatical Range and Accuracy: range, accuracy, punctuation and sentence control.
If the task requires at least 250 words and the response is under 250, reflect this
in Task Response feedback and score. Do not automatically fail an underlength essay.
For each error, quote the student's exact words and give a clear correction. Keep
errors focused and useful; do not rewrite every sentence. Distinguish stylistic
suggestions from actual grammar errors. Do not grade an empty or unreadable response.
Scores are estimates for practice, not official IELTS results.
"""
    user_payload = {
        "assignment_title": assignment_title,
        "task_question_and_instructions": assignment_instructions,
        "student_response": response[:24000],
        "calculated_word_count": word_count,
    }
    try:
        raw = _chat_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ], json_mode=True)
        result = json.loads(raw)
        criteria = result.get("criteria") or {}
        keys = ("task_response", "coherence_cohesion", "lexical_resource", "grammatical_range_accuracy")
        labels = {
            "task_response": "Task Response",
            "coherence_cohesion": "Coherence and Cohesion",
            "lexical_resource": "Lexical Resource",
            "grammatical_range_accuracy": "Grammatical Range and Accuracy",
        }
        scores, normalized = [], {}
        for key in keys:
            item = criteria.get(key) or {}
            score = round(max(0.0, min(9.0, float(item.get("score", 0)))) * 2) / 2
            scores.append(score)
            normalized[key] = {"label": labels[key], "score": score, "feedback": str(item.get("feedback", ""))[:1600]}
        overall = math.floor((sum(scores) / len(scores)) * 2 + 0.5) / 2
        errors = result.get("errors", [])
        if not isinstance(errors, list):
            errors = []
        return {
            "status": "completed", "overall_band": overall, "word_count": word_count,
            "criteria": normalized, "errors": errors[:35],
            "strengths": result.get("strengths", [])[:8],
            "priority_improvements": result.get("priority_improvements", [])[:8],
            "overall_feedback": str(result.get("overall_feedback", ""))[:3000],
            "suggested_rewrite": str(result.get("suggested_rewrite", ""))[:1000],
            "notice": "AI-generated IELTS practice estimate only. This is not an official IELTS result.",
        }
    except Exception as exc:
        return {
            "status": "failed",
            "notice": "AI assessment could not be completed. Your work is saved for teacher review.",
            "detail": str(exc)[:500],
        }


def score_subjective(skill, prompt, response):
    """Optional AI scoring for timed speaking/writing practice responses."""
    if not _api_key() or not response.strip():
        return None, "AI scoring is not configured. Your response has been saved for teacher review."
    try:
        raw = _chat_completion([
            {"role": "system", "content": (
                "You are an IELTS practice assessor. Return JSON with band_score (0-9), "
                "strengths (array), improvements (array), concise_feedback (string). "
                "For writing consider task response, coherence, lexical resource and grammar. "
                "For speaking transcripts consider fluency/coherence, vocabulary and grammar. "
                "Do not claim to assess pronunciation from plain text. Practice estimate only."
            )},
            {"role": "user", "content": json.dumps({
                "skill": skill, "practice_prompt": prompt, "student_response": response
            }, ensure_ascii=False)},
        ])
        parsed = json.loads(raw)
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
