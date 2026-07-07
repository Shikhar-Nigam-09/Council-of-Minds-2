import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.schemas.agent_response import AgentResponse
from app.services.agents.base_agent import BaseAgent
from app.services.agents.logical_agent import LogicalAgent
from app.services.agents.practical_agent import PracticalAgent
from app.services.agents.rational_agent import RationalAgent
from app.services.agents.skeptical_agent import SkepticalAgent
from app.services.agents.spiritual_agent import SpiritualAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the parallel execution of the five specialized reasoning agents
    using asyncio.gather() with per-agent timeout and error isolation.
    """

    def __init__(self):
        self.agents: List[BaseAgent] = [
            LogicalAgent(),
            RationalAgent(),
            PracticalAgent(),
            SpiritualAgent(),
            SkepticalAgent(),
        ]

    async def _run_single_agent(
        self,
        agent: BaseAgent,
        question: str,
        context_chunks: List[str],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentResponse:
        """Runs a single agent wrapped in asyncio.wait_for timeout."""
        start_time = time.perf_counter()
        try:
            return await asyncio.wait_for(
                agent.respond(question, context_chunks, conversation_history),
                timeout=settings.AGENT_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = f"Agent '{agent.name}' timed out after {settings.AGENT_TIMEOUT_SECONDS}s"
            logger.error(error_msg)
            return AgentResponse(
                agent_name=agent.name,
                answer="",
                key_points=[],
                self_reported_confidence=0.0,
                latency_ms=elapsed_ms,
                error=error_msg,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = f"Agent '{agent.name}' encountered unexpected error: {exc}"
            logger.error(error_msg, exc_info=True)
            return AgentResponse(
                agent_name=agent.name,
                answer="",
                key_points=[],
                self_reported_confidence=0.0,
                latency_ms=elapsed_ms,
                error=error_msg,
            )

    async def run_agents(
        self,
        question: str,
        context_chunks: List[str],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[AgentResponse]:
        """
        Executes all five reasoning agents concurrently.

        Ensures that if any individual agent fails or times out, the error is isolated
        into an AgentResponse object and does not fail the batch.
        """
        start_total = time.perf_counter()
        logger.info(
            f"Orchestrator launching {len(self.agents)} agents in parallel for question: '{question[:50]}...'"
        )

        tasks = [
            self._run_single_agent(
                agent, question, context_chunks, conversation_history
            )
            for agent in self.agents
        ]

        # Use return_exceptions=True for robust error isolation across the batch
        results = await asyncio.gather(*tasks, return_exceptions=True)

        responses: List[AgentResponse] = []
        for i, res in enumerate(results):
            agent = self.agents[i]
            if isinstance(res, Exception):
                # Fallback in case an exception somehow escaped _run_single_agent
                elapsed_ms = (time.perf_counter() - start_total) * 1000.0
                err_msg = f"Unhandled exception in agent '{agent.name}': {res}"
                logger.error(err_msg, exc_info=True)
                responses.append(
                    AgentResponse(
                        agent_name=agent.name,
                        answer="",
                        key_points=[],
                        self_reported_confidence=0.0,
                        latency_ms=elapsed_ms,
                        error=err_msg,
                    )
                )
            else:
                responses.append(res)

        for r in responses:
            logger.info(
                f"[Diagnostic Orchestrator] agent_name='{r.agent_name}', "
                f"answer_present={bool(r.answer and r.answer.strip())}, "
                f"answer_length={len(r.answer)}, "
                f"error={r.error}, "
                f"parsed_confidence={r.self_reported_confidence}"
            )

        total_elapsed_ms = (time.perf_counter() - start_total) * 1000.0
        success_count = sum(
            1
            for r in responses
            if r.error is None and bool(r.answer and r.answer.strip())
        )
        logger.info(
            f"Orchestrator completed batch: {success_count}/{len(self.agents)} succeeded in {total_elapsed_ms:.2f}ms total."
        )
        return responses


agent_orchestrator = AgentOrchestrator()
