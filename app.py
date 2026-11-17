import json
import os
from flask import Flask, render_template, request
from google import genai
from google.genai import types

app = Flask(__name__)

# Перед завантаженням на GitHub поверни текст 'ВСТАВ_СЮДИ_КЛЮЧ', а справжній ключ додай у налаштування хостингу!
API_KEY = os.environ.get("GEMINI_API_KEY", "ВСТАВ_СЮДИ_КЛЮЧ")


def generate_startup_idea(topic: str) -> dict:
    client = genai.Client(api_key=API_KEY)

    prompt = (
        f"Ти — досвідчений венчурний аналітик і креативний директор. "
        f"Придумай оригінальну, реалістичну ідею технологічного стартапу у сфері: «{topic}». "
        f"Відповідь дай українською мовою у форматі JSON з такими полями:\n"
        f'- "name": коротка яскрава назва стартапу (1-2 слова)\n'
        f'- "slogan": влучний рекламний слоган (1 речення)\n'
        f'- "description": суть проєкту та яку проблему він вирішує (2-3 речення)\n'
        f'- "audience": цільова аудиторія (1 речення)\n'
        f'- "monetization": модель монетизації / як проєкт заробляє (1 речення)'
    )

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.8,
        ),
    )

    return json.loads(response.text)


@app.route("/", methods=["GET", "POST"])
def index():
    startup = None
    error = None
    topic = ""

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        if not topic:
            error = "Будь ласка, введіть або оберіть тему для стартапу."
        elif API_KEY == "ВСТАВ_СЮДИ_КЛЮЧ" or not API_KEY:
            error = "Не вказано API-ключ Gemini. Додайте його в app.py або змінні середовища."
        else:
            try:
                startup = generate_startup_idea(topic)
            except Exception as e:
                error = f"Помилка під час звернення до ШІ: {str(e)}"

    return render_template("index.html", startup=startup, error=error, topic=topic)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)