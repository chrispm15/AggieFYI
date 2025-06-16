import openai
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
class OpenAIEmbedder:
    def __call__(self, input):
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=input
        )
        raw = [r["embedding"] for r in response["data"]]
        normalized = [self._normalize(vec) for vec in raw]
        return normalized

    def _normalize(self, vec):
        norm = np.linalg.norm(vec)
        return [v / norm for v in vec] if norm > 0 else vec

    def name(self):
        return "openai-embedding-3-small"
