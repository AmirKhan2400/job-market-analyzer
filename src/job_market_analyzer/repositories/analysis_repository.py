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
    ) -> int:

        analysis = AnalysisMapper.to_model(jobAnalysis)

        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)

        return analysis.id

    def get_all(self) -> list[JobAnalysis]:
        models = self.session.query(AnalysisModel).all()
        return AnalysisMapper.to_domain_list(models)

    def delete(self, analysis: AnalysisModel) -> None:
        self.session.delete(analysis)
        self.session.commit()

    def delete_by_id(self, analysis_id: int) -> None:
        analysis = self.session.get(AnalysisModel, analysis_id)

        if analysis is not None:
            self.session.delete(analysis)
            self.session.commit()
