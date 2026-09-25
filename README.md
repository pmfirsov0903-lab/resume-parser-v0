# Resume Parser v0

Інструмент командного рядка: папка резюме (PDF/DOCX) + одна вакансія → структуровані
JSON-профілі кандидатів → оцінка відповідності 0–100 з поясненням → підсумковий CSV-рейтинг.

Деталі підходу — у [SPEC.md](SPEC.md).

## Встановлення

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

## Налаштування

1. Скопіюй `.env.example` у `.env` і встав свій ключ Anthropic API:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

   За потреби зміни модель через `RESUME_PARSER_MODEL` (за замовчуванням `claude-opus-5`).

2. Поклади резюме (`.pdf` / `.docx`) у папку `resumes/`.

3. Опиши вакансію у `vacancy.json` (приклад — `vacancy.example.json`):

   ```bash
   cp vacancy.example.json vacancy.json
   ```

   Поля: `title`, `must_have_skills[]`, `nice_to_have_skills[]`, `min_years_experience`, `description`.

## Запуск

```bash
python -m src.pipeline
```

Опційні прапорці: `--resumes <папка>`, `--vacancy <файл>`, `--out <папка>` (за замовчуванням
`resumes/`, `vacancy.json`, `out/`).

> **Windows-нотатка:** якщо українські символи в консолі виглядають як "кракозябри",
> запусти `chcp 65001` перед командою або встанови `set PYTHONIOENCODING=utf-8` —
> на файли (`out/*.json`, `out/ranking.csv`) це не впливає, вони завжди в UTF-8.

## Результат

- `out/profiles/<файл>.json` — структурований профіль кожного кандидата.
- `out/scores/<файл>.json` — оцінка 0–100 з поясненням для кожного кандидата.
- `out/ranking.csv` — підсумкова таблиця `filename, name, score, top_reason`,
  відсортована за оцінкою (від найвищої до найнижчої).

## Обмеження v0

- Без OCR — скановані PDF без текстового шару позначаються як `extraction_failed` і пропускаються.
- Одна вакансія на прогін.
- Тільки CLI, без веб-інтерфейсу.
