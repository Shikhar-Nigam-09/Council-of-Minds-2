import abc
import logging
import time
from typing import Any, Dict, List, Optional

from app.schemas.agent_response import AgentResponse
from app.services.llm.groq_client import groq_client

logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """
    Abstract base class for specialized reasoning agents.

    Each agent embodies a distinct persona and evaluates questions + retrieved context
    completely decoupled from database or FAISS retrieval logic.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique identifier name of the agent (e.g., 'logical')."""
        pass

    @property
    @abc.abstractmethod
    def persona_prompt(self) -> str:
        """The system prompt defining the agent's persona and reasoning style."""
        pass

    async def respond(
        self,
        question: str,
        context_chunks: List[str],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentResponse:
        """
        Executes reasoning over the provided question and context chunks.

        Note: `conversation_history` is accepted for forward-compatibility with
        Phase 7, but is currently unused by these five Phase 5 agents.
        """
        start_time = time.perf_counter()
        logger.info(f"Agent '{self.name}' starting evaluation...")

        # Format context chunks
        formatted_context = "\n\n".join(
            [f"[Chunk {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)]
        )
        if not formatted_context.strip():
            formatted_context = "(No retrieved context provided)"

        history_text = ""
        if conversation_history:
            turns = [
                f"[{turn.get('role', 'user').upper()}]: {turn.get('content', '')}"
                for turn in conversation_history
            ]
            history_text = (
                "\n\nRecent Conversation History (for resolving follow-up references ONLY):\n"
                + "\n".join(turns)
                + "\n\nCRITICAL INSTRUCTION: Prioritize Retrieved Context Evidence over conversational assumptions. "
                "Conversation history is provided strictly to resolve pronoun references and follow-up intent (e.g., 'what about the second point?'). "
                "DO NOT substitute conversational assumptions for document evidence."
            )

        user_prompt = (
            f"Question:\n{question}\n\n"
            f"Retrieved Context Evidence:\n{formatted_context}"
            f"{history_text}\n\n"
            "Please analyze the question using your specialized reasoning style based on the evidence provided above. "
            "Respond ONLY with a valid JSON object containing exactly these fields:\n"
            '- "answer": string (your comprehensive analysis)\n'
            '- "key_points": list of strings (3 to 5 bullet points)\n'
            '- "self_reported_confidence": float between 0.0 and 1.0 (your internal confidence self-estimate based on the evidence)\n'
        )

        try:
            raw_json = await groq_client.generate_json(
                system_prompt=self.persona_prompt,
                user_prompt=user_prompt,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            answer = str(raw_json.get("answer", ""))
            key_points = raw_json.get("key_points", [])
            if not isinstance(key_points, list):
                key_points = [str(key_points)] if key_points else []
            key_points = [str(kp) for kp in key_points]

            conf_val = None
            for k in [
                "self_reported_confidence",
                "confidence",
                "confidence_score",
                "self_confidence",
                "score",
            ]:
                if k in raw_json and raw_json[k] is not None:
                    conf_val = raw_json[k]
                    break

            if conf_val is None:
                logger.warning(
                    f"Agent '{self.name}' JSON missing confidence field. Returned keys: {list(raw_json.keys())}. Defaulting to 0.0."
                )
                conf = 0.0
            else:
                try:
                    if isinstance(conf_val, str):
                        conf_val = conf_val.strip().rstrip("%")
                    conf = float(conf_val)
                    if conf > 1.0 and conf <= 100.0:
                        conf = conf / 100.0
                    conf = max(0.0, min(1.0, conf))
                except (ValueError, TypeError) as exc:
                    logger.warning(
                        f"Agent '{self.name}' returned malformed confidence '{conf_val}': {exc}. Defaulting to 0.0."
                    )
                    conf = 0.0

            logger.info(
                f"[Diagnostic BaseAgent] agent_name='{self.name}', "
                f"answer_present={bool(answer and answer.strip())}, "
                f"answer_length={len(answer)}, "
                f"error=None, "
                f"returned_keys={list(raw_json.keys())}, "
                f"parsed_confidence={conf}"
            )

            logger.info(
                f"Agent '{self.name}' completed successfully in {elapsed_ms:.2f}ms (confidence: {conf:.2f})"
            )
            return AgentResponse(
                agent_name=self.name,
                answer=answer,
                key_points=key_points,
                self_reported_confidence=conf,
                latency_ms=elapsed_ms,
                error=None,
            )

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"Agent '{self.name}' failed after {elapsed_ms:.2f}ms: {exc}",
                exc_info=True,
            )
            logger.info(
                f"[Diagnostic BaseAgent] agent_name='{self.name}', "
                f"answer_present=False, "
                f"answer_length=0, "
                f"error='{str(exc)}', "
                f"returned_keys=[], "
                f"parsed_confidence=0.0"
            )
            return AgentResponse(
                agent_name=self.name,
                answer="",
                key_points=[],
                self_reported_confidence=0.0,
                latency_ms=elapsed_ms,
                error=str(exc),
            )
