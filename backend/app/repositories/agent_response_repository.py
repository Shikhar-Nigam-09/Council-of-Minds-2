import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_response import AgentResponse as AgentResponseModel
from app.models.message_evidence import MessageEvidence as MessageEvidenceModel
from app.schemas.agent_response import AgentResponse as AgentResponseSchema
from app.schemas.council_response import ChunkRef


class AgentResponseRepository:
    """Repository layer for creating agent evaluation outputs and evidence links."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_batch(
        self,
        message_id: uuid.UUID | str,
        responses: List[AgentResponseSchema],
        commit: bool = True,
    ) -> List[AgentResponseModel]:
        """Persist a batch of agent persona responses or challenger critiques."""
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)

        models = []
        for res in responses:
            model = AgentResponseModel(
                message_id=message_id,
                agent_name=res.agent_name,
                answer=res.answer,
                key_points=res.key_points,
                self_reported_confidence=res.self_reported_confidence,
                latency_ms=res.latency_ms,
            )
            self.session.add(model)
            models.append(model)

        if commit:
            await self.session.commit()
            for m in models:
                await self.session.refresh(m)
        else:
            await self.session.flush()
        return models

    async def create_evidence_batch(
        self,
        message_id: uuid.UUID | str,
        chunk_refs: List[ChunkRef],
        commit: bool = True,
    ) -> List[MessageEvidenceModel]:
        """Persist a batch of document evidence links for an assistant message."""
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)

        models = []
        for ref in chunk_refs:
            if ref.chunk_id is None:
                continue
            cid = ref.chunk_id
            if isinstance(cid, str):
                try:
                    cid = uuid.UUID(cid)
                except ValueError:
                    continue
            model = MessageEvidenceModel(
                message_id=message_id,
                chunk_id=cid,
                similarity_score=ref.similarity_score,
            )
            self.session.add(model)
            models.append(model)

        if commit:
            await self.session.commit()
            for m in models:
                await self.session.refresh(m)
        else:
            await self.session.flush()
        return models
