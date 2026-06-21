# ═══════════════════════════════════════════════════════════════
# inference.py — The AI Voice
# ═══════════════════════════════════════════════════════════════
# This is the bridge that actually talks to your local AI model
# (running privately on your own hardware via Ollama). It packages
# up the cleaned user question, the facts from the Retriever,
# and the AI's personality instructions, then asks the AI to
# generate the response.
# ═══════════════════════════════════════════════════════════════

"""
Ravel — Stage 5: SLM Inference (Small Language Model)
Sends the processed prompt to an AI model (via Ollama) and gets the response.

Key features:
- Supports ANY Ollama-compatible model (Llama, Mistral, Phi, etc.)
- Applies Chain-of-Thought wrapping for complex queries (from EASE routing)
- Dynamically switches endpoints/models per persona ("skin")
- Prepends system prompts and user memories to personalize responses
"""

import httpx  # Async HTTP client — used to call the Ollama API
import json
from pipeline import PipelineContext
import config


class SLMInference:
    """Stage 5: Calls the AI model to generate a response.

    "SLM" = Small Language Model (e.g., Llama 3 8B, Mistral 7B, Phi-3)
    These run locally via Ollama — no cloud API needed, data stays private.
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)  # 60s timeout for slow models
        self.base_url = config.OLLAMA_BASE_URL          # Default Ollama endpoint

    def _wrap_cot(self, prompt: str) -> str:
        """Wrap the prompt with Chain-of-Thought instructions.
        
        This tells the AI: "Think step by step before answering."
        Research shows this improves accuracy on complex questions significantly.
        Only applied when EASE routes the query to COT or BORDERLINE."""
        return (
            "Think through this step by step before answering.\n"
            "First, identify the key aspects of the question.\n"
            "Then, reason through each aspect carefully.\n"
            "Finally, provide a clear and concise answer.\n\n"
            f"{prompt}"
        )

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Send the prompt to the AI model and get a response. Called by the Pipeline."""
        # Use the RAG-augmented prompt if available, otherwise the sanitized input
        user_prompt = ctx.augmented_prompt or ctx.sanitized_input

        # If EASE decided this is a complex query, add chain-of-thought instructions
        if ctx.ease_route in ("COT", "BORDERLINE"):
            user_prompt = self._wrap_cot(user_prompt)

        # Build the final prompt by combining: system prompt + memories + user question
        prompt_parts = []
        if ctx.system_prompt:
            prompt_parts.append(ctx.system_prompt)       # Persona instructions ("You are...")
        if ctx.formatted_memories:
            prompt_parts.append(ctx.formatted_memories)  # User's saved memories/facts
        prompt_parts.append(user_prompt)                 # The actual question
        prompt = "\n\n".join(prompt_parts)

        # Use custom endpoint/model if set by the persona, otherwise use defaults
        ollama_url = ctx.ollama_endpoint if ctx.ollama_endpoint else self.base_url
        model = ctx.model_name if ctx.model_name else config.MODEL_NAME

        try:
            # Call Ollama's /api/generate endpoint
            response = await self.client.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,  # Wait for full response (not streaming)
                    "options": {
                        "temperature": config.MODEL_TEMPERATURE,  # Creativity (0 = deterministic)
                        "num_predict": config.MODEL_MAX_TOKENS,    # Max response length
                        "num_ctx": 4096,                           # Context window size
                    },
                },
            )

            if response.status_code == 200:
                data = response.json()
                ctx.slm_response = data.get("response", "").strip()
                # Note: Ollama doesn't return per-token probabilities by default,
                # so DoLa (next stage) will use its estimation approach instead
                ctx.logprobs = []
            else:
                ctx.slm_response = (
                    f"SLM inference failed (status {response.status_code}). "
                    "Please ensure Ollama is running."
                )

        except httpx.ConnectError:
            # Ollama isn't running or wrong URL
            ctx.slm_response = (
                "Could not connect to SLM backend. "
                "Please ensure Ollama is running on "
                f"{ollama_url}"
            )
        except Exception as e:
            ctx.slm_response = f"Inference error: {str(e)}"

        return ctx

    async def close(self):
        """Clean up the HTTP client when the server shuts down."""
        await self.client.aclose()
