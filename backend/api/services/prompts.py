# Builds reusable prompts for AI grading and nature-code classification.

# Standard library
import textwrap
from typing import Dict, Any

# Third party
from pathlib import Path

# Local modules
from api.services.text_handler import json_to_text

NATURE_KEYWORDS_MASTER_PATH = Path("data") / "nature_keywords_master.json"

def _format_question_sequence(questions_dict: Dict[str, Dict[str, Any]]) -> str:
    """Format protocol questions into a compact sequence for the grading prompt."""
    lines = []

    for q_id, q in questions_dict.items():
        # Do not include skipped questions in displayed sequence
        if q.get("Skip_AI_Grading", False):
            continue

        question_id = q.get("Question_ID", q_id)
        question_text = q.get("Question_Text", "").strip()

        lines.append(f"- {question_id}: {question_text}")

    return "\n".join(lines)

def get_grading_system_prompt(transcript_text, questions_dict):
    """Build the system prompt used for per-question transcript grading."""
    return (
        f"{GRADING_BASE_PROMPT}\n\n"
        f"CALL TRANSCRIPT:\n{transcript_text}\n\n"
        f"CORRECT QUESTION SEQUENCE:\n{_format_question_sequence(questions_dict)}"
    )


def get_single_question_prompt(question: Dict[str, Any]) -> str:
    """Provide question metadata; shared grading rules are in the system prompt."""
    fields = (
        ("Parent ID", "Parent_Question_ID"),
        ("Question ID", "Question_ID"),
        ("Text", "Question_Text"),
        ("Allowed Alternatives", "Allowed_Alternatives"),
        ("Condition", "Condition"),
        ("Situation", "Situation"),
        ("Scenario", "Scenario"),
    )
    lines = ["Grade ONLY this question using the supplied transcript and rules:"]
    for label, key in fields:
        value = question.get(key)
        lines.append(f"{label}: {'None' if value is None else value}")
    return "\n".join(lines)


def get_nature_code_prompt(transcript_path, nature_codes_master):
    """Build the prompt used to classify a transcript into a nature code."""
    # Load transcript text
    transcript_text = json_to_text(file_path=transcript_path)

    # Format nature codes cleanly
    formatted_codes = []

    for code_id, code_data in nature_codes_master.items():
        # Skip case entry
        if str(code_id) == "0":
            continue

        nature_code_name = code_data.get("nature_code_name", "Unknown")
        classification = code_data.get("classification", {})
        keywords = classification.get("keywords", []) or []
        # common_confusions = classification.get("common_confusions", []) or []

        keyword_text = ", ".join(map(str, keywords)) if keywords else "None"

        formatted_codes.append(f"[{code_id}] {nature_code_name}: {keyword_text}")

    nature_codes_text = "\n".join(formatted_codes)
    return (
        f"{NATURE_CODE_PROMPT}\n\n"
        f"AVAILABLE NATURE CODES (ID, name: keywords):\n{nature_codes_text}\n\n"
        f"TRANSCRIPT:\n{transcript_text}"
    )

GRADING_BASE_PROMPT = textwrap.dedent("""
    Grade one EMS/911 protocol question against the transcript and correct question sequence.
    Use only transcript evidence; do not invent dialogue or infer intent. Evaluate strictly:
    protocol compliance overrides conversational naturalness. Consider surrounding context
    only to determine whether an explicit Condition is met.

    Assign exactly one code:
    [1] Asked Correctly: asked in order with meaning and intent preserved.
    [2] Not Asked: required question omitted.
    [3] Asked Incorrectly: wording changes meaning/intent, including leading, biased,
        or incomplete phrasing. Takes priority over incorrect order.
    [4] Not As Scripted: acceptable meaning, but out of order.
    [5] Not Applicable: ONLY when an explicit Condition is unmet by transcript evidence.
    [6] Obvious: caller directly and plainly stated the answer to this exact question,
        requiring no assumption, inference, interpretation, or surrounding context,
        and dispatcher appropriately did not ask again.

    Questions are required by default. Without an unmet explicit Condition, an omission
    is [2], unless [6] applies. Redundancy or apparent lack of necessity does not justify [5].
    Use the supplied question metadata and Allowed Alternatives when evaluating wording.

    Speaker labels may be wrong. Reinterpret speaker identity only when the exchange
    strongly suggests mislabeling (e.g., dispatcher answering their own question).
    Do not penalize labeling errors or invent dialogue; retain original labels in quotes.

    Output: [code] followed by concise, specific reasoning and direct supporting quotes.
    Each quote must include the original speaker label, timestamp, and exact wording.
    No paraphrased quotes, JSON, bullets, sections, extra formatting, or other grades.
""").strip()

NATURE_CODE_PROMPT = textwrap.dedent("""
    Select exactly one available Nature Code for this EMS/911 transcript.
    Use only explicit transcript evidence and the full event timeline. Prioritize the
    initiating event/root cause over downstream symptoms, even if the cause is clarified
    later: fall then vomiting -> Falls; allergy then breathing difficulty -> Allergic
    Reaction; substance exposure then symptoms -> Hazmat/Inhalation.
    With no clear mechanism, choose the best-fitting symptom code. If causes compete,
    choose the best-supported cause. Keywords guide classification; context and event
    sequence matter more than keyword matches. Give one decisive final classification.

    Output:
    [ID]
    Reasoning:
    - Concise explanation supported by transcript details and/or keywords.
    Possible Confusions:
    - For each of 2-3 plausible alternatives: nature code name, why it could apply,
      and why it is incorrect. Consider symptom/cause confusion, similar categories,
      and overlapping keywords.
""").strip()
