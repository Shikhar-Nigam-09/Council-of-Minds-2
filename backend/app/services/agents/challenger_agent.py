import logging
from typing import List

from app.core.config import settings
from app.schemas.council_response import ChallengeCritique
from app.services.llm.groq_client import groq_client

logger = logging.getLogger(__name__)


class ChallengerAgent:
    """
    Rigorously reviews and critiques the Aggregator's synthesized answer against retrieved context chunks
    using Llama 3.3 70B, surfacing caveats, unsupported claims, and missing considerations.
    """

    async def critique(
        self,
        question: str,
        aggregated_answer: str,
        context_chunks: List[str],
        is_empty_retrieval: bool = False,
    ) -> ChallengeCritique:
        """
        Generates a structured critique of the aggregated answer.
        """
        logger.info("[Challenger Runtime] Challenger started.")
        logger.info(
            f"[Challenger Runtime] Selected model: {settings.AGGREGATOR_MODEL_NAME}"
        )
        if not aggregated_answer or not aggregated_answer.strip():
            return ChallengeCritique(
                critique_summary="No aggregated answer provided to critique.",
                weaknesses=[],
                unsupported_claims=[],
                missing_considerations=[],
            )

        context_text = "\n\n".join(
            f"[Chunk {i+1}]: {c}"
            for i, c in enumerate(context_chunks)
            if c and c.strip()
        )
        if not context_text or is_empty_retrieval:
            context_text = "[No supporting document chunks were retrieved from the knowledge base.]"

        system_prompt = (
            "You are the Challenger Agent of the Council of Minds, powered by Llama 3.3 70B.\n"
            "Your critical mission is to act as an intellectual red-teamer and rigorous peer reviewer for the synthesized answer.\n\n"
            "GUIDELINES:\n"
            "1. Be Genuinely Critical: Do not rubber-stamp or restate the answer. Identify real logical vulnerabilities, empirical gaps, and assumptions.\n"
            "2. Check Evidence Support: Compare claims made in the answer against the retrieved context chunks. Flag any claim that is unsupported by or contradicts the evidence.\n"
            "3. Identify Blind Spots: Surfacing edge cases, risks, or alternative interpretations overlooked by the council.\n"
            "4. If no document chunks were retrieved, ensure the answer explicitly acknowledged this and did not invent document facts.\n\n"
            "Return your critique as a JSON object with EXACTLY the following keys:\n"
            '- "critique_summary": A concise 2-4 sentence overall summary of your critique.\n'
            '- "weaknesses": A list of strings detailing logical or empirical weaknesses.\n'
            '- "unsupported_claims": A list of strings detailing claims not backed by the retrieved context chunks.\n'
            '- "missing_considerations": A list of strings detailing important considerations or caveats overlooked.'
        )

        user_prompt = (
            f"Original Question: {question}\n\n"
            f"Retrieved Context Chunks:\n{context_text}\n\n"
            f"Synthesized Answer to Critique:\n{aggregated_answer}\n\n"
            "Please generate your structured critique now."
        )

        try:
            result = await groq_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=settings.AGGREGATOR_MODEL_NAME,
                temperature=0.5,
            )
            summary = result.get("critique_summary", "Critique completed.")
            weaknesses = result.get("weaknesses", [])
            unsupported_claims = result.get("unsupported_claims", [])
            missing_considerations = result.get("missing_considerations", [])

            crit_generated = bool(summary and summary != "Critique completed.")
            logger.info(
                f"[Challenger Runtime] Critique generated: {crit_generated}, weaknesses count: {len(weaknesses)}, unsupported claims count: {len(unsupported_claims)}"
            )

            return ChallengeCritique(
                critique_summary=summary,
                weaknesses=weaknesses,
                unsupported_claims=unsupported_claims,
                missing_considerations=missing_considerations,
            )
        except Exception as exc:
            logger.error(f"Challenger LLM call failed: {exc}", exc_info=True)
            return ChallengeCritique(
                critique_summary=f"[Critique Error]: Unable to generate critique due to LLM service failure: {exc}",
                weaknesses=[],
                unsupported_claims=[],
                missing_considerations=[],
            )


challenger_agent = ChallengerAgent()
