"""Minimal OpenAI client wrapper used by the generator and tests.

This module tries to initialize the official OpenAI v1 client when an API key
is provided. If the import or initialization fails (for example during unit
tests or when the package is not installed), the class still exists and
generate_caption falls back to a deterministic local string so tests remain
fast and offline.
"""
from typing import Optional


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.client = None
        if api_key:
            try:
                import openai

                # Use new v1 client if available. If import fails, we silently
                # continue with client=None so tests don't require network libs.
                try:
                    self.client = openai.OpenAI(api_key=api_key)
                except Exception:
                    # If the installed openai package doesn't have v1 style,
                    # leave client as None.
                    self.client = None
            except Exception:
                self.client = None

    def generate_caption(self, product_name: str, price: float, affiliate_link: str) -> str:
        """Generate a short caption for a product.

        If the underlying OpenAI client isn't configured, return a deterministic
        fallback caption suitable for tests and offline runs.
        """
        if not self.client:
            return f"{product_name} only {price:.2f}! Buy now: {affiliate_link}"

        # Attempt a chat completion with the v1 client. Keep errors local so
        # caller can fall back as needed.
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Create a short social-media caption for the product: {product_name} "
                            f"priced at {price:.2f}. Include a call-to-action and a short set of hashtags."
                        ),
                    }
                ],
                max_tokens=64,
            )
            # v1 response shape: resp.choices[0].message.content
            return resp.choices[0].message.content
        except Exception:
            # On any error, return a fallback caption
            return f"{product_name} only {price:.2f}! Buy here: {affiliate_link}"
