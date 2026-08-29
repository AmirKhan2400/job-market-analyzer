from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from job_market_analyzer.database.session import Base


class AnalysisModel(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    visitor_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    company: Mapped[str | None] = mapped_column(String, nullable=True)

    role: Mapped[str] = mapped_column(String)

    score: Mapped[float] = mapped_column(Float)

    decision: Mapped[str] = mapped_column(String)

    reason_to_apply: Mapped[str] = mapped_column(String)

    matched_skills: Mapped[str] = mapped_column(String)

    missing_skills: Mapped[str] = mapped_column(String)

    required_skills: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
