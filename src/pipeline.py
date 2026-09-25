"""CLI: папка резюме + вакансія -> JSON-профілі, оцінки, підсумковий CSV-рейтинг та HTML-звіт."""

import argparse
import csv
import json
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from .extract import SUPPORTED_EXTENSIONS, extract_text
from .llm import build_profile, score_profile
from .models import Vacancy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resume Parser v0 — оцінка резюме проти вакансії"
    )
    parser.add_argument(
        "--resumes", type=Path, default=Path("resumes"), help="Папка з резюме (PDF/DOCX)"
    )
    parser.add_argument(
        "--vacancy", type=Path, default=Path("vacancy.json"), help="JSON-файл вакансії"
    )
    parser.add_argument(
        "--out", type=Path, default=Path("out"), help="Папка для результатів"
    )
    return parser.parse_args()


def load_vacancy(path: Path) -> Vacancy:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Vacancy(**data)


def export_html_report(out_path: Path, rows: list, vacancy_title: str) -> None:
    """Генерує красивий HTML-звіт з результатами ранжування."""
    html_content = f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Рейтинг кандидатів — {vacancy_title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f5f7; color: #333; margin: 0; padding: 30px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
        h1 {{ color: #111; font-size: 24px; margin-bottom: 5px; }}
        .subtitle {{ color: #666; font-size: 14px; margin-bottom: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 14px 16px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }}
        th {{ background-color: #fafbfc; font-weight: 600; color: #444; }}
        tr:hover {{ background-color: #f8fafc; }}
        .score-badge {{ display: inline-block; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 13px; text-align: center; }}
        .score-high {{ background-color: #e6f4ea; color: #137333; }}
        .score-mid {{ background-color: #fef7e0; color: #b06000; }}
        .score-low {{ background-color: #fce8e6; color: #c5221f; }}
        .score-none {{ background-color: #f1f3f4; color: #5f6368; }}
        .reason {{ color: #555; line-height: 1.4; }}
        .filename {{ font-family: monospace; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Результати скринінгу резюме</h1>
        <div class="subtitle">Вакансія: <strong>{vacancy_title}</strong></div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 60px;">#</th>
                    <th style="width: 200px;">Кандидат / Файл</th>
                    <th style="width: 90px; text-align: center;">Бали</th>
                    <th>Обґрунтування / Вердикт</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, row in enumerate(rows, 1):
        score = row["score"]
        if isinstance(score, int):
            if score >= 75:
                badge_class = "score-high"
            elif score >= 50:
                badge_class = "score-mid"
            else:
                badge_class = "score-low"
            score_text = str(score)
        else:
            badge_class = "score-none"
            score_text = "N/A"

        html_content += f"""
                <tr>
                    <td><strong>{idx}</strong></td>
                    <td>
                        <div style="font-weight: 600; font-size: 15px;">{row['name'] or 'Не вказано'}</div>
                        <div class="filename">{row['filename']}</div>
                    </td>
                    <td style="text-align: center;"><span class="score-badge {badge_class}">{score_text}</span></td>
                    <td class="reason">{row['full_reason']}</td>
                </tr>
"""

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    out_path.write_text(html_content, encoding="utf-8")


def main() -> None:
    load_dotenv()
    args = parse_args()

    if not args.vacancy.exists():
        raise SystemExit(f"Файл вакансії не знайдено: {args.vacancy}")
    if not args.resumes.exists():
        raise SystemExit(f"Папку з резюме не знайдено: {args.resumes}")

    args.out.mkdir(parents=True, exist_ok=True)
    profiles_dir = args.out / "profiles"
    scores_dir = args.out / "scores"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    scores_dir.mkdir(parents=True, exist_ok=True)

    vacancy = load_vacancy(args.vacancy)
    client = anthropic.Anthropic()

    resume_files = sorted(
        p for p in args.resumes.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not resume_files:
        print(f"У папці {args.resumes} не знайдено PDF/DOCX файлів.")
        return

    rows = []
    for path in resume_files:
        print(f"Обробка: {path.name}")

        try:
            text = extract_text(path)
        except Exception as e:
            print(f"  Помилка витягу тексту: {e}")
            rows.append(
                {
                    "filename": path.name,
                    "name": "",
                    "score": "",
                    "full_reason": f"Помилка витягу тексту: {e}",
                }
            )
            continue

        if not text.strip():
            print("  Порожній текстовий шар (можливо, скан без OCR) — пропускаю.")
            rows.append(
                {
                    "filename": path.name,
                    "name": "",
                    "score": "",
                    "full_reason": "Порожній текстовий шар (extraction failed: empty text layer)",
                }
            )
            continue

        try:
            profile = build_profile(client, text, path.name)
            (profiles_dir / f"{path.stem}.json").write_text(
                profile.model_dump_json(indent=2), encoding="utf-8"
            )

            result = score_profile(client, profile, vacancy)
            (scores_dir / f"{path.stem}.json").write_text(
                result.model_dump_json(indent=2), encoding="utf-8"
            )

            rows.append(
                {
                    "filename": path.name,
                    "name": profile.name,
                    "score": result.score,
                    "full_reason": result.explanation,
                }
            )
        except Exception as e:
            print(f"  Помилка обробки LLM: {e}")
            rows.append(
                {
                    "filename": path.name,
                    "name": "",
                    "score": "",
                    "full_reason": f"Помилка LLM: {e}",
                }
            )

    rows.sort(key=lambda r: r["score"] if isinstance(r["score"], int) else -1, reverse=True)

    # 1. Зберігаємо CSV (з utf-8-sig для Excel)
    ranking_csv_path = args.out / "ranking.csv"
    with ranking_csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "name", "score", "top_reason"])
        writer.writeheader()
        for r in rows:
            top_reason = r["full_reason"].splitlines()[0][:200] if r["full_reason"] else ""
            writer.writerow({
                "filename": r["filename"],
                "name": r["name"],
                "score": r["score"],
                "top_reason": top_reason
            })

    # 2. Генеруємо HTML-звіт
    ranking_html_path = args.out / "ranking.html"
    export_html_report(ranking_html_path, rows, vacancy.title)

    print(f"\nГотово!")
    print(f" - CSV рейтинг: {ranking_csv_path}")
    print(f" - HTML-звіт:  {ranking_html_path}")


if __name__ == "__main__":
    main()