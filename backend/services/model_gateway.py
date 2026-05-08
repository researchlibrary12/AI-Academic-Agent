from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from config import settings


class ModelGateway:
    """Provider abstraction for OpenAI/Anthropic model switching."""

    def __init__(self) -> None:
        self._openai = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self._anthropic = (
            AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        )

    async def generate(self, prompt: str) -> str:
        if settings.model_provider == "anthropic":
            if not self._anthropic:
                raise RuntimeError("ANTHROPIC_API_KEY is required when MODEL_PROVIDER=anthropic")
            response = await self._anthropic.messages.create(
                model=settings.model_name,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0]
            return getattr(content, "text", "")

        if not self._openai:
            raise RuntimeError("OPENAI_API_KEY is required when MODEL_PROVIDER=openai")

        response = await self._openai.responses.create(
            model=settings.model_name,
            input=prompt,
        )
        return response.output_text

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self._openai:
            raise RuntimeError("OPENAI_API_KEY is required for embeddings")
        response = await self._openai.embeddings.create(model=settings.embedding_model, input=texts)
        return [row.embedding for row in response.data]

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self.embed_texts([text])
        return vectors[0]


model_gateway = ModelGateway()
