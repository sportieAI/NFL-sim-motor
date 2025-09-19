"""
Generative Commentary Engine
Leverages OpenAI or HuggingFace LLMs for play-by-play and color commentary.
"""

import os

try:
    import openai
except ImportError:
    openai = None


class GenerativeCommentary:
    def __init__(self, model="gpt-3.5-turbo", temperature=0.8):
        self.model = model
        self.temperature = temperature
        if openai:
            openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate(self, play_summary: str, context: dict = None) -> str:
        prompt = (
            f"As an elite NFL commentator, narrate this play with drama and insight: {play_summary} "
            "Add tactical and emotional depth. One or two sentences max."
        )
        if openai:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative, insightful sports commentator.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=90,
                temperature=self.temperature,
            )
            return response.choices[0].message["content"].strip()
        else:
            return f"[AI Commentary]: {play_summary} (Install openai for full feature)"


# Usage: commentator = GenerativeCommentary(); text = commentator.generate("Mahomes escapes pressure, throws deep TD.")
