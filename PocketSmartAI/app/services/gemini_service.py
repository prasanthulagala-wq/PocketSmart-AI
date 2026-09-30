import json
from typing import Any
from io import BytesIO
from ..config import settings
from .fallback import fallback_recommendation

class GeminiService:
    def __init__(self):
        self.client = None
        if settings.gemini_api_key:
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)

    def _prompt(self, planner: str, data: dict) -> str:
        return f"""You are PocketSmart AI, a careful budget planning assistant.
Planner: {planner}
User input JSON: {json.dumps(data, ensure_ascii=False)}

Create practical recommendations that respect the user's maximum budget. Do not claim that a product is currently in stock or that a price is live unless verified. Platform names are discovery destinations, not proof of availability. Return ONLY valid JSON matching this structure:
{{
  "planner": "{planner}", "title": "string", "summary": "string", "budget": integer,
  "estimated_total": integer, "remaining_budget": integer,
  "allocations": [{{"category":"string","amount":integer,"percentage":number,"note":"string"}}],
  "recommendations": [{{"name":"string","category":"string","estimated_price":integer,"platform":"Amazon|Flipkart|IKEA|Swiggy|Zomato|OYO|Other","url":"string","reason":"string","quantity":integer}}],
  "tips": ["string"]
}}
Use Indian Rupees. Keep recommendations useful and realistic. Never exceed the budget in estimated_total. For URLs, use platform search URLs when an exact item URL is unavailable."""

    def generate(self, planner: str, data: dict, image_bytes: bytes | None = None, mime_type: str | None = None) -> dict:
        if not self.client:
            return fallback_recommendation(planner, data["budget"], data)
        from google.genai import types
        contents: list[Any] = [self._prompt(planner, data)]
        if image_bytes and mime_type:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
            contents.append("Use the uploaded outfit image only as visual context for color/style coordination.")
        try:
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                ),
            )
            parsed = getattr(response, "parsed", None)
            if parsed is not None:
                result = parsed.model_dump() if hasattr(parsed, "model_dump") else parsed
            else:
                result = json.loads(response.text)
            return self._normalize(result, planner, data)
        except Exception:
            return fallback_recommendation(planner, data["budget"], data)

    def _normalize(self, result: dict, planner: str, data: dict) -> dict:
        result["planner"] = planner
        result["budget"] = data["budget"]
        result.setdefault("allocations", [])
        result.setdefault("recommendations", [])
        result.setdefault("tips", [])
        for item in result["recommendations"]:
            item.setdefault("quantity", 1)
            item.setdefault("platform", "Other")
            item.setdefault("url", "https://www.google.com/search?q=" + item.get("name", "PocketSmart" ).replace(" ", "+"))
        result["estimated_total"] = min(int(result.get("estimated_total", 0)), data["budget"])
        result["remaining_budget"] = max(0, data["budget"] - result["estimated_total"])
        return result

gemini_service = GeminiService()
