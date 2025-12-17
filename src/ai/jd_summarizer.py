from groq import Groq
import os
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.utils.contants import SUMMARY_SYSTEM_PROMPT

logger = get_logger(__name__)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_jd(jd_text: str) -> str:
    if not isinstance(jd_text, str) or len(jd_text.strip()) == 0 or len(jd_text) < 100:
        return ""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # 🔥 recommended
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": jd_text}
            ],
            temperature=0.2,
            max_tokens=200,
        )
        result = resp.choices[0].message.content.strip()
        logger.info(f"result: {result}")

        return result

    except Exception as e:
        print("Groq error:", e)
        return ""
