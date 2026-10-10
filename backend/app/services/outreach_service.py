"""Outreach business logic: approval gate, sending, opt-out enforcement."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, ConflictError, NotFoundError
from app.integrations.email.factory import get_email_provider
from app.models.enums import FollowupState, LeadStatus, OutreachStatus
from app.models.outreach import Outreach
from app.repositories.lead_repository import LeadRepository
from app.repositories.outreach_repository import OutreachRepository
from app.schemas.outreach import OutreachPrepareRequest
from app.utils.validators import can_transition


class OutreachService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = OutreachRepository(session)
        self.leads = LeadRepository(session)
        self.session = session

    async def prepare(self, owner_id: UUID, data: OutreachPrepareRequest) -> Outreach:
        lead = await self.leads.get_by_id(data.lead_id, owner_id)
        if lead is None:
            raise NotFoundError("LEAD_NOT_FOUND", "The requested lead does not exist.")
        if lead.status == LeadStatus.DO_NOT_CONTACT.value:
            raise AppError("OPTED_OUT", "Lead opted out; outreach is not allowed.", 403)
        if not lead.personalized_message:
            raise ConflictError(
                "NO_MESSAGE",
                "Run the personalization agent before preparing outreach.",
            )
        outreach = Outreach(
            lead_id=lead.id,
            campaign_id=data.campaign_id,
            owner_id=owner_id,
            channel=data.channel,
            subject=f"Quick thought for {lead.company_name}",
            body=lead.personalized_message,
            status=OutreachStatus.PENDING_APPROVAL.value,
        )
        await self.repo.add(outreach)
        await self.session.commit()
        return outreach

    async def get(self, owner_id: UUID, outreach_id: UUID) -> Outreach:
        outreach = await self.repo.get_by_id(outreach_id, owner_id)
        if outreach is None:
            raise NotFoundError("OUTREACH_NOT_FOUND", "The requested outreach does not exist.")
        return outreach

    async def approve(self, owner_id: UUID, outreach_id: UUID) -> Outreach:
        outreach = await self.get(owner_id, outreach_id)
        if outreach.status not in {
            OutreachStatus.PREPARED.value,
            OutreachStatus.PENDING_APPROVAL.value,
        }:
            raise AppError(
                "INVALID_OUTREACH_STATE",
                f"Outreach in status {outreach.status} cannot be approved.",
                422,
            )
        outreach.status = OutreachStatus.APPROVED.value
        outreach.approved_at = datetime.now(UTC)
        await self.session.commit()
        return outreach

    async def send(self, owner_id: UUID, outreach_id: UUID) -> Outreach:
        outreach = await self.get(owner_id, outreach_id)
        if outreach.status != OutreachStatus.APPROVED.value:
            raise AppError(
                "APPROVAL_REQUIRED",
                "Outreach must be approved by a human before sending.",
                409,
            )
        lead = await self.leads.get_by_id(outreach.lead_id, owner_id)
        if lead is None:
            raise NotFoundError("LEAD_NOT_FOUND", "The requested lead does not exist.")
        if lead.status == LeadStatus.DO_NOT_CONTACT.value:
            raise AppError("OPTED_OUT", "Lead opted out; outreach is not allowed.", 403)
        if not lead.email:
            raise ConflictError("NO_EMAIL", "This lead has no email address.")

        try:
            await get_email_provider().send_email(
                to=lead.email,
                subject=outreach.subject or "Follow-up",
                body=outreach.body,
            )
        except Exception as exc:  # noqa: BLE001 - provider failure becomes a state, not a crash
            outreach.status = OutreachStatus.FAILED.value
            outreach.error = "Email provider failed to send the message."
            await self.session.commit()
            raise AppError("SEND_FAILED", "The email could not be sent.", 502) from exc

        outreach.status = OutreachStatus.SENT.value
        outreach.sent_at = datetime.now(UTC)
        outreach.error = None
        if can_transition(lead.status, LeadStatus.CONTACTED.value):
            lead.status = LeadStatus.CONTACTED.value
        await self.session.commit()
        return outreach

    async def list(
        self,
        owner_id: UUID,
        *,
        lead_id: UUID | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Outreach], int]:
        return await self.repo.list(
            owner_id, lead_id=lead_id, status=status, page=page, page_size=page_size
        )

    async def opt_out(self, owner_id: UUID, lead_id: UUID) -> None:
        lead = await self.leads.get_by_id(lead_id, owner_id)
        if lead is None:
            raise NotFoundError("LEAD_NOT_FOUND", "The requested lead does not exist.")
        lead.status = LeadStatus.DO_NOT_CONTACT.value
        lead.followup_state = FollowupState.DO_NOT_CONTACT.value

        pending, _ = await self.repo.list(owner_id, lead_id=lead_id, page_size=100)
        for outreach in pending:
            if outreach.status in {
                OutreachStatus.PREPARED.value,
                OutreachStatus.PENDING_APPROVAL.value,
                OutreachStatus.APPROVED.value,
            }:
                outreach.status = OutreachStatus.OPTED_OUT.value
        await self.session.commit()
