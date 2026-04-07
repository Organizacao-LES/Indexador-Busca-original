from sqlalchemy.orm import Session

from app.pipeline.pipeline_stage import PipelineStage


class DocumentIngestionPipeline:
    def __init__(self, stages: list[PipelineStage]):
        self.stages = stages

    def run(self, db: Session, context: dict) -> dict:
        for stage in self.stages:
            context = stage.execute(db, context)
        return context
