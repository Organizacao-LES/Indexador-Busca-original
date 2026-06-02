from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class PipelineStage(ABC):
    @abstractmethod
    def execute(self, db: Session, context: dict) -> dict:
        raise NotImplementedError
