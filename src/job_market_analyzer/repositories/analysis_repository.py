from sqlalchemy.orm import Session

from job_market_analyzer.database.models import AnalysisModel
from job_market_analyzer.domain.analysis import JobAnalysis
from job_market_analyzer.mappers.analysis_mapper import AnalysisMapper


class AnalysisRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(
        self,
        jobAnalysis: JobAnalysis,
        visitor_id: str,
    ) -> int:

        analysis = AnalysisMapper.to_model(jobAnalysis, visitor_id=visitor_id)

        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)

        return analysis.id

    def get_all(self) -> list[JobAnalysis]:
        models = self.session.query(AnalysisModel).all()
        return AnalysisMapper.to_domain_list(models)

    def get_all_by_visitor_id(self, visitor_id: str) -> list[JobAnalysis]:
        models = (
            self.session.query(AnalysisModel)
            .filter(AnalysisModel.visitor_id == visitor_id)
            .order_by(AnalysisModel.created_at.desc())
            .all()
        )
        return AnalysisMapper.to_domain_list(models)

    def delete(self, analysis: AnalysisModel) -> None:
        self.session.delete(analysis)
        self.session.commit()

    def delete_by_id(self, analysis_id: int) -> None:
        analysis = self.session.get(AnalysisModel, analysis_id)

        if analysis is not None:
            self.session.delete(analysis)
            self.session.commit()
