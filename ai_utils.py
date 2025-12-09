import os
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _format_history_for_prompt(history_entries, max_items=30):
    """Turn history list into a compact text summary for the model."""
    lines = []
    for entry in history_entries[:max_items]:
        ts = entry["timestamp"]
        if isinstance(ts, datetime):
            ts_str = ts.strftime("%Y-%m-%d %H:%M")
        else:
            ts_str = str(ts)

        lines.append(
            f"- {ts_str}: {entry['details']}"
        )
    if not lines:
        return "No sensor readings yet."
    return "\n".join(lines)


def get_history_ai_insights(history_entries, user=None):
    """
    Returns a short AI-generated summary + recommendations string.
    """
    formatted = _format_history_for_prompt(history_entries)

    user_context = ""
    if user is not None:
        user_context = (
            f"User hair type: {user.hair_type or 'unknown'}.\n"
            f"User purpose: {user.purpose or 'unspecified'}.\n"
        )

    prompt = f"""
You are a helpful, gentle scalp and hair health assistant for a Black hair–focused app.
You see a series of scalp sensor readings (temperature, moisture, etc.).
Give a short summary and a few practical, non-medical suggestions.

NEVER give medical advice. If something sounds serious, say they should
consult a dermatologist or trichologist.

User context:
{user_context}

Recent sensor history:
{formatted}

Provide your answer in this structure:

Summary:
- one or two bullet points

Recommendations:
- 3–5 short bullet points, friendly, practical, and easy to act on.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system",
             "content": "You are an assistant focused on scalp moisture, comfort, and hair health. You speak simply and kindly."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def get_insights_page_ai(readings_last_7_days, user=None):
    """
    Higher-level insights for the /insights page.
    readings_last_7_days: list of dicts with temperature, moisture_percent, timestamp.
    """
    if not readings_last_7_days:
        return "I don’t see any sensor data yet. Try wearing your device for a few days so I can learn your patterns."

    lines = []
    for r in readings_last_7_days[:50]:
        ts = r["timestamp"]
        if isinstance(ts, datetime):
            ts_str = ts.strftime("%Y-%m-%d %H:%M")
        else:
            ts_str = str(ts)

        temp = r.get("temperature")
        moist = r.get("moisture_percent")
        lines.append(f"- {ts_str}: temp={temp}°C, moisture={moist}%")

    user_context = ""
    if user is not None:
        user_context = (
            f"User hair type: {user.hair_type or 'unknown'}.\n"
            f"User purpose: {user.purpose or 'unspecified'}.\n"
        )

    prompt = f"""
You are a scalp and hair health insights assistant for a Black hair–focused app.
You have about a week of sensor readings (temperature and moisture).

User context:
{user_context}

Last 7 days of sensor data:
{chr(10).join(lines)}

Give:
1) A short explanation of general patterns (is moisture low, stable, fluctuating?).
2) A simple hydration or care recommendation tailored to this pattern.
3) A few ideas for routines or habits to try.

Avoid any medical advice. Encourage professional help if irritation,
pain, or hair loss is persistent.

Use headings like:

Overview:
- ...

Hydration & Comfort:
- ...

Routine Ideas:
- ...
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system",
             "content": "You give friendly, practical scalp and hair care insights, without medical advice."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
