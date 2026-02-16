from google import genai
from .config import GEMINI_API_KEY

class AIAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            # We don't raise here to allow the bot to start even if key is missing (for testing purposes),
            # but methods will fail. Ideally should log warning.
            pass

        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception:
            self.client = None

        self.model = "gemini-2.0-flash"

    async def _generate(self, prompt: str) -> str:
        if not self.client:
            return "Error: GEMINI_API_KEY is missing or invalid. Please check your configuration."

        try:
            # Use async client via self.client.aio
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt
            )
            if response.text:
                return response.text
            return "Error: No response generated."
        except Exception as e:
            return f"Error connecting to AI service: {str(e)}"

    async def generate_client_finding_strategy(self, business_type: str, target_audience: str) -> str:
        prompt = (
            f"You are a direct, no-nonsense business consultant named 'Pool Saz'. "
            f"The user has a business: '{business_type}'. Target audience: '{target_audience}'. "
            f"Provide 3 actionable, specific strategies to find clients immediately. "
            f"Then, provide 2 ready-to-use outreach templates (one for email/DM, one for cold calling/messaging). "
            f"Focus on conversion. Do not use motivational fluff. "
            f"Language: Persian. Tone: Professional, Direct."
        )
        return await self._generate(prompt)

    async def generate_sales_text(self, product_details: str) -> str:
        prompt = (
            f"You are a sales copywriter expert. "
            f"The product is: '{product_details}'. "
            f"Write 2 high-converting sales text templates. "
            f"1. A short, punchy version for social media captions. "
            f"2. A longer, detailed version for email or landing page. "
            f"Include a strong Call to Action (CTA). Remove all fluff. "
            f"Language: Persian. Tone: Persuasive, Urgent."
        )
        return await self._generate(prompt)

    async def generate_content_ideas(self, content_type: str) -> str:
        prompt = (
            f"You are a content strategist. "
            f"The user wants content ideas for: '{content_type}'. "
            f"Provide 5 high-engagement content ideas/titles. "
            f"For each idea, provide a brief outline or key points to cover. "
            f"Focus on value and virality. "
            f"Language: Persian."
        )
        return await self._generate(prompt)
