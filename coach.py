import re

FILLERS = {
    "um",
    "uh",
    "like",
    "actually",
    "basically",
    "literally",
    "you know",
    "i mean",
}

STAR_WORDS = {
    "situation": ["situation", "context", "problem", "challenge"],
    "task": ["task", "goal", "responsibility", "needed"],
    "action": ["action", "built", "created", "implemented", "fixed", "improved"],
    "result": ["result", "impact", "outcome", "learned", "reduced", "increased"],
}


def words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def count_fillers(text: str) -> int:
    clean_text = " " + " ".join(words(text)) + " "
    total = 0
    for filler in FILLERS:
        if " " in filler:
            total += clean_text.count(f" {filler} ")
        else:
            total += words(text).count(filler)
    return total


def score_answer(question: str, transcript: str) -> dict:
    tokens = words(transcript)
    word_count = len(tokens)
    filler_count = count_fillers(transcript)

    star_hits = {
        part: any(keyword in tokens for keyword in keywords)
        for part, keywords in STAR_WORDS.items()
    }
    star_score = sum(star_hits.values()) * 15
    length_score = min(25, round(word_count / 4))
    clarity_score = max(0, 25 - filler_count * 3)
    score = min(100, star_score + length_score + clarity_score)

    tips = []
    if word_count < 45:
        tips.append("Add more detail. Aim for a 60 to 90 second answer.")
    if not star_hits["situation"]:
        tips.append("Start with the situation or problem so the listener has context.")
    if not star_hits["action"]:
        tips.append("Explain your specific actions, not only the team effort.")
    if not star_hits["result"]:
        tips.append("End with a measurable result or what you learned.")
    if filler_count > 3:
        tips.append("Reduce filler words by pausing for one second before answering.")
    if not tips:
        tips.append("Good structure. Now make the result more specific with numbers.")

    return {
        "question": question,
        "score": score,
        "word_count": word_count,
        "filler_count": filler_count,
        "star": star_hits,
        "tips": tips[:4],
        "summary": build_summary(score, word_count, filler_count),
    }


def build_summary(score: int, word_count: int, filler_count: int) -> str:
    if score >= 80:
        level = "strong"
    elif score >= 55:
        level = "decent"
    else:
        level = "needs work"
    return f"This answer is {level}: {word_count} words with {filler_count} filler words."
