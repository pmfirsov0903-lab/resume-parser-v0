"""Виклики Claude API: структуризація резюме у JSON-профіль та оцінка проти вакансії."""

import json
import anthropic
from .models import ResumeProfile, ScoreResult, Vacancy

MODEL = "claude-sonnet-5"

PROFILE_SYSTEM_PROMPT = """\
Ти — інструмент для структуризації резюме. Отримавши сирий текст резюме, витягни інформацію про кандидата суворо за заданою схемою JSON.
Повертай ВИКЛЮЧНО валідний JSON без жодних додаткових пояснень чи текстів, загорнутий у блоки ```json ... ``` або просто у вигляді JSON.

Правила:
- Якщо якесь поле не знайдено в тексті — залиш його порожнім (null для опційних полів, порожній список для списків). Не вигадуй дані.
- years_experience: оціни загальну кількість років релевантного досвіду роботи на основі дат у work_history. Якщо дат недостатньо — залиш null.
- Пиши текстові поля мовою оригіналу резюме, не перекладай.
"""

SCORE_SYSTEM_PROMPT = """\
Ти — асистент з оцінки відповідності кандидата вакансії. Тобі дають структурований профіль кандидата (JSON) і вимоги вакансії (JSON). Оцени відповідність за шкалою 0–100.
Повертай ВИКЛЮЧНО валідний JSON, що відповідає схемі ScoreResult (повинен містити поля score та explanation).
"""

def _extract_text_from_response(response) -> str:
    """Безпечно витягує текст із відповіді Claude, ігноруючи блокові міркування (ThinkingBlock)."""
    for block in response.content:
        if hasattr(block, "text") and block.text:
            return block.text
    raise ValueError(response.content)


def _clean_and_parse_json(raw_text: str, model_class):
    """Очищує текст від Markdown-обгорток, адаптує ключі та парсить через Pydantic."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    clean_json = text.strip()

    data = json.loads(clean_json)
    
    if isinstance(data, dict):
        if model_class is ResumeProfile:
            if "full_name" in data and "name" not in data:
                data["name"] = data["full_name"]
                
            if "contacts" not in data or not isinstance(data["contacts"], dict):
                data["contacts"] = {
                    "name": data.get("name") or data.get("full_name"),
                    "email": data.get("email"),
                    "phone": data.get("phone")
                }
            else:
                if "full_name" in data["contacts"] and "name" not in data["contacts"]:
                    data["contacts"]["name"] = data["contacts"]["full_name"]

            if "work_history" in data and isinstance(data["work_history"], list):
                for item in data["work_history"]:
                    if isinstance(item, dict):
                        if "title" not in item:
                            item["title"] = item.get("position") or item.get("role") or "Developer"
                        if "period" not in item:
                            item["period"] = item.get("dates") or item.get("duration") or "N/A"
                        if "description" not in item:
                            item["description"] = item.get("details") or item.get("summary") or ""

        elif model_class is ScoreResult:
            if "score" not in data:
                data["score"] = data.get("overall_score") or data.get("points") or 0
                
            if "explanation" not in data:
                data["explanation"] = (
                    data.get("verdict") 
                    or data.get("reasoning") 
                    or data.get("summary") 
                    or "Оцінка сформована автоматично без детального пояснення."
                )

    return model_class.model_validate(data)


def build_profile(client: anthropic.Anthropic, resume_text: str, filename: str) -> ResumeProfile:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=PROFILE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Текст резюме (файл {filename}):\n\n{resume_text}",
            }
        ],
    )
    raw_text = _extract_text_from_response(response)
    return _clean_and_parse_json(raw_text, ResumeProfile)


def score_profile(
    client: anthropic.Anthropic, profile: ResumeProfile, vacancy: Vacancy
) -> ScoreResult:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SCORE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Вакансія:\n{vacancy.model_dump_json(indent=2)}\n\n"
                    f"Профіль кандидата:\n{profile.model_dump_json(indent=2)}"
                ),
            }
        ],
    )
    raw_text = _extract_text_from_response(response)
    return _clean_and_parse_json(raw_text, ScoreResult)