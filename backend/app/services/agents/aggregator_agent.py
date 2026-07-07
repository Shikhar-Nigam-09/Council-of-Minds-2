import logging
import math
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.schemas.agent_response import AgentResponse
from app.services.llm.groq_client import groq_client

logger = logging.getLogger(__name__)

KNOWN_PERSONAS = {"logical", "rational", "practical", "spiritual", "skeptical"}


class AggregatorAgent:
    """
    Synthesizes outputs from the five reasoning personas into a single coherent final answer
    using Llama 3.3 70B, respecting normalized per-agent weights.
    """

    def _validate_and_normalize_weights(
        self,
        raw_weights: Optional[Dict[str, float]],
        successful_agents: List[AgentResponse],
    ) -> Dict[str, float]:
        """
        Validates raw weights and normalizes them across successful agents.

        Validation rules:
        - Only known persona names
        - Finite numeric values
        - Non-negative
        - At least one successful agent with weight > 0
        """
        weights = raw_weights or settings.DEFAULT_AGENT_WEIGHTS

        # Validate keys and values
        for k, v in weights.items():
            if k not in KNOWN_PERSONAS:
                raise ValueError(
                    f"Unknown persona name in agent_weights: '{k}'. Must be one of {KNOWN_PERSONAS}."
                )
            if not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError(
                    f"Weight for persona '{k}' must be a finite numeric value (got {v})."
                )
            if v < 0:
                raise ValueError(
                    f"Weight for persona '{k}' must be non-negative (got {v})."
                )

        # Exclude failed/timed-out agents and build map for successful agents
        succ_names = {res.agent_name for res in successful_agents}
        succ_weights = {
            name: float(
                weights.get(name, settings.DEFAULT_AGENT_WEIGHTS.get(name, 1.0))
            )
            for name in succ_names
        }

        total_weight = sum(succ_weights.values())
        if total_weight <= 0:
            raise ValueError(
                f"At least one successful agent must have a weight > 0. Successful agents: {list(succ_names)}, weights: {succ_weights}"
            )

        # Normalize across successful agents so sum == 1.0
        normalized = {
            name: round(w / total_weight, 4) for name, w in succ_weights.items()
        }
        logger.debug(
            f"Normalized aggregator weights across successful agents: {normalized}"
        )
        return normalized

    async def aggregate(
        self,
        question: str,
        agent_responses: List[AgentResponse],
        agent_weights: Optional[Dict[str, float]] = None,
        is_empty_retrieval: bool = False,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Synthesizes successful agent responses into a unified final answer.
        """
        successful_agents = [
            res
            for res in agent_responses
            if res.error is None and res.answer and res.answer.strip()
        ]
        failed_count = len(agent_responses) - len(successful_agents)
        logger.info(
            f"[Aggregator Runtime] Aggregator started. Received {len(successful_agents)} successful agents, {failed_count} failed agents."
        )
        logger.info(
            f"[Aggregator Runtime] Selected model: {settings.AGGREGATOR_MODEL_NAME}"
        )

        if not successful_agents:
            logger.warning(
                "All reasoning agents failed or returned empty answers. Aggregator returning fallback."
            )
            return "I am unable to synthesize an answer because all reasoning personas failed or timed out during evaluation."

        normalized_weights = self._validate_and_normalize_weights(
            agent_weights, successful_agents
        )

        # Build agent summaries for prompt
        agent_sections = []
        for res in successful_agents:
            w = normalized_weights.get(res.agent_name, 0.0)
            key_pts = (
                "\n    - ".join(res.key_points) if res.key_points else "None listed"
            )
            section = (
                f"### Persona: {res.agent_name.upper()} (Assigned Emphasis Weight: {w * 100:.1f}%)\n"
                f"- **Answer**: {res.answer}\n"
                f"- **Key Points**:\n    - {key_pts}\n"
            )
            agent_sections.append(section)

        agents_text = "\n".join(agent_sections)

        empty_retrieval_notice = ""
        if is_empty_retrieval:
            empty_retrieval_notice = (
                "\nCRITICAL NOTICE: No supporting document evidence was retrieved from the RAG knowledge base for this query. "
                "You must explicitly acknowledge that no document evidence was retrieved, rely strictly on general reasoning or persona logic, "
                "and MUST NOT invent, hallucinate, or claim document-grounded facts.\n"
            )

        history_text = ""
        if conversation_history:
            turns = [
                f"[{turn.get('role', 'user').upper()}]: {turn.get('content', '')}"
                for turn in conversation_history
            ]
            history_text = (
                "\n\nRecent Conversation History:\n"
                + "\n".join(turns)
                + "\n\nNote: Maintain conversational continuity with prior turns, but ensure document-grounded evidence takes precedence over conversational assumptions."
            )

        system_prompt = (
            "You are the Aggregator Agent of the Council of Minds, powered by Llama 3.3 70B.\n"
            "Your role is to synthesize the perspectives of five specialized reasoning personas "
            "(Logical, Rational, Practical, Spiritual, Skeptical) into ONE unified, coherent, and comprehensive final answer.\n\n"
            "GUIDELINES:\n"
            "1. Respect Assigned Emphasis Weights: Give more influence and prominence to personas with higher weights. "
            "If a persona has 0% weight, ignore their perspective unless critical for safety.\n"
            "2. Synthesize, Do Not List: Write a seamless, structured response rather than merely listing what each persona said.\n"
            "3. Resolve Conflicts: Where personas disagree (e.g. Practical vs. Spiritual), explain the tension and provide a balanced resolution.\n"
            f"{empty_retrieval_notice}\n"
            'Return your synthesized answer in a JSON object with a single string key: "aggregated_answer".'
        )

        user_prompt = (
            f"Question: {question}\n\n"
            f"Successful Persona Responses & Weights:\n{agents_text}"
            f"{history_text}\n\n"
            "Please synthesize these into the final aggregated answer now."
        )

        try:
            result = await groq_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=settings.AGGREGATOR_MODEL_NAME,
                temperature=0.4,
            )
            ans = result.get("aggregated_answer", "").strip()
            if not ans:
                # Fallback if model returned different key or empty string
                ans = str(result.get("answer", str(result)))
            logger.info(
                f"[Aggregator Runtime] Final answer present: {bool(ans and ans.strip())}, length: {len(ans)}"
            )
            return ans
        except Exception as exc:
            logger.error(f"Aggregator LLM call failed: {exc}", exc_info=True)
            return f"[Synthesis Error]: Unable to aggregate responses due to LLM service failure: {exc}"


aggregator_agent = AggregatorAgent()
