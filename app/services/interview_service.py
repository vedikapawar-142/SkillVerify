"""AI Technical Interview Service.
Utilizes Google Gemini API with fallback NLP rubric engine.
Evaluates candidate answers across Technical Correctness (40%), Relevance (30%), and Clarity (30%).
"""
import os
import re
import json
import logging
from typing import List, Dict, Any
from flask import current_app
from ..models import db, InterviewQA, Attempt
from .llm import ask_llm

logger = logging.getLogger(__name__)

CURATED_INTERVIEW_QUESTIONS = [
    {
        "id": 1,
        "topic": "Memory Management & Data Structures",
        "question": "How does Python handle memory management and garbage collection? Explain the difference between reference counting and the cyclic garbage collector.",
        "key_concepts": ["reference counting", "garbage collection", "cyclic", "gc", "deallocation", "memory", "generation", "circular reference"]
    },
    {
        "id": 2,
        "topic": "Concurrency & Python Internals",
        "question": "What is the Global Interpreter Lock (GIL) in CPython, and what impact does it have on CPU-bound vs. I/O-bound multithreaded applications?",
        "key_concepts": ["gil", "global interpreter lock", "cpython", "thread", "cpu-bound", "io-bound", "multiprocessing", "concurrency"]
    },
    {
        "id": 3,
        "topic": "Python Iterators & Generators",
        "question": "Explain the difference between an iterator and a generator in Python. When would you use the 'yield' statement instead of returning a list?",
        "key_concepts": ["yield", "generator", "iterator", "memory", "lazy evaluation", "iter", "next", "streaming", "iterable"]
    }
]


def get_interview_questions(role_title: str = "Python Developer") -> List[Dict[str, Any]]:
    """Retrieve 3 technical interview questions via Gemini API or fallback curated bank."""
    api_key = ""
    try:
        api_key = current_app.config.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY", "")

    if api_key:
        prompt = (
            f"You are a technical interview examiner for a {role_title} position. "
            "Generate 3 focused technical interview questions testing Python fundamentals, architecture, and memory/concurrency. "
            "Reply ONLY with a raw JSON array of objects without markdown formatting: "
            "[{\"id\": 1, \"topic\": \"Topic Name\", \"question\": \"Question text?\", \"key_concepts\": [\"term1\", \"term2\"]}]"
        )
        try:
            reply = ask_llm(prompt)
            clean_reply = reply.strip()
            if clean_reply.startswith("```"):
                clean_reply = clean_reply.split("```")[1]
                if clean_reply.startswith("json"):
                    clean_reply = clean_reply[4:]
            clean_reply = clean_reply.strip()
            questions = json.loads(clean_reply)
            if isinstance(questions, list) and len(questions) >= 3:
                return questions[:3]
        except Exception as e:
            logger.warning(f"Gemini interview question generation failed: {e}. Using curated question bank.")

    return CURATED_INTERVIEW_QUESTIONS


def evaluate_interview_response(question_text: str, answer_text: str, key_concepts: List[str] = None) -> Dict[str, Any]:
    """Evaluate candidate response using Gemini API or rule-based rubric scoring.
    Rubric: Technical Correctness (0-40), Relevance (0-30), Conceptual Clarity (0-30).
    """
    clean_ans = (answer_text or "").strip()
    if not clean_ans:
        return {
            "score": 0.0,
            "rubric": {"correctness": 0, "relevance": 0, "clarity": 0},
            "feedback": "No answer was provided for this question.",
            "engine": "Automated Evaluation Engine"
        }

    api_key = ""
    try:
        api_key = current_app.config.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY", "")

    # Try Gemini evaluation first
    if api_key:
        prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer.\n"
            f"Question: {question_text}\n"
            f"Candidate Answer: {clean_ans}\n\n"
            "Evaluate the answer strictly based on this rubric:\n"
            "- technical_correctness (0 to 40)\n"
            "- relevance (0 to 30)\n"
            "- clarity (0 to 30)\n"
            "Total score is sum of the three (0 to 100).\n"
            "Reply ONLY in valid JSON format without markdown:\n"
            "{\"score\": 85, \"rubric\": {\"correctness\": 35, \"relevance\": 25, \"clarity\": 25}, \"feedback\": \"Constructive evaluation here...\"}"
        )
        try:
            reply = ask_llm(prompt)
            clean_reply = reply.strip()
            if clean_reply.startswith("```"):
                clean_reply = clean_reply.split("```")[1]
                if clean_reply.startswith("json"):
                    clean_reply = clean_reply[4:]
            clean_reply = clean_reply.strip()
            result = json.loads(clean_reply)
            result["engine"] = "Google Gemini AI Evaluator"
            return result
        except Exception as e:
            logger.warning(f"Gemini evaluation failed: {e}. Using local rubric evaluator.")

    # Local Rubric Evaluator Fallback
    words = clean_ans.split()
    word_count = len(words)
    ans_lower = clean_ans.lower()

    if not key_concepts:
        # Extract keywords from question
        q_words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", question_text)]
        key_concepts = list(set(q_words[:8]))

    # 1. Relevance: presence of key concepts (0-30)
    matched_concepts = [c for c in key_concepts if c.lower() in ans_lower]
    relevance_ratio = min(1.0, len(matched_concepts) / max(1, len(key_concepts) * 0.5))
    relevance_score = round(relevance_ratio * 30.0, 1)

    # 2. Technical Correctness (0-40)
    # Scaled by depth and key concepts
    depth_factor = min(1.0, word_count / 40.0)
    correctness_score = round((relevance_ratio * 0.7 + depth_factor * 0.3) * 40.0, 1)

    # 3. Clarity & Structure (0-30)
    # Sentences, explanation connectors ('because', 'while', 'for example', 'difference', 'in order to')
    connectors = ["because", "while", "for example", "difference", "whereas", "such as", "therefore", "instead", "means"]
    connector_count = sum(1 for c in connectors if c in ans_lower)
    clarity_ratio = min(1.0, (word_count >= 25) * 0.5 + min(0.5, connector_count * 0.15))
    clarity_score = round(clarity_ratio * 30.0, 1)

    total_score = round(correctness_score + relevance_score + clarity_score, 1)

    feedback_parts = []
    if total_score >= 75:
        feedback_parts.append("Strong technical response with sound conceptual foundation and clear terminology.")
    elif total_score >= 50:
        feedback_parts.append("Adequate response demonstrating foundational understanding; consider providing deeper architectural examples.")
    else:
        feedback_parts.append("Basic response. More specific terminology and detailed explanation of underlying mechanics recommended.")

    if matched_concepts:
        feedback_parts.append(f"Demonstrated awareness of: {', '.join(matched_concepts[:4])}.")

    return {
        "score": total_score,
        "rubric": {
            "correctness": correctness_score,
            "relevance": relevance_score,
            "clarity": clarity_score
        },
        "feedback": " ".join(feedback_parts),
        "engine": "Automated Rubric Evaluation (Fallback NLP Engine)"
    }


def record_interview_qa(attempt_id: int, question_text: str, answer_text: str, key_concepts: List[str] = None) -> InterviewQA:
    """Evaluate and store an interview Q&A session in database."""
    evaluation = evaluate_interview_response(question_text, answer_text, key_concepts)
    
    qa = InterviewQA(
        attempt_id=attempt_id,
        question_text=question_text,
        answer_text=answer_text,
        score=evaluation.get("score", 0.0),
        feedback=evaluation.get("feedback", ""),
        rubric_evaluation=json.dumps(evaluation.get("rubric", {}))
    )
    db.session.add(qa)
    db.session.commit()
    return qa
