def detect_weak_topics(records: list[dict[str, float | str]]) -> list[dict[str, object]]:
    weak = []
    for row in records:
        topic = str(row.get("topic", "Unknown"))
        score = float(row.get("score", 0))
        max_score = max(float(row.get("max_score", 100)), 1.0)
        pct = round((score / max_score) * 100, 2)
        if pct < 50:
            weak.append(
                {
                    "topic": topic,
                    "percentage": pct,
                    "priority": "high",
                    "recommendation": f"{topic} is weak. Focus daily for the next 2 weeks.",
                }
            )
    return weak
