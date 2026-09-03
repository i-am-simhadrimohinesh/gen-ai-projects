from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Journey(Base):

    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    goal: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    existing_knowledge: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    topics: Mapped[list["Topic"]] = relationship(
        back_populates="journey",
        cascade="all, delete-orphan",
        order_by="Topic.order",
    )

    assessments: Mapped[list["Assessment"]] = relationship(
    back_populates="journey",
    cascade="all, delete-orphan",
    )

    learner_knowledge: Mapped[list["LearnerKnowledge"]] = relationship(
    back_populates="journey",
    cascade="all, delete-orphan",
)


class Topic(Base):

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    journey_id: Mapped[int] = mapped_column(
        ForeignKey("journeys.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    completed: Mapped[bool] = mapped_column(
    default=False,
    nullable=False,
    )

    journey: Mapped["Journey"] = relationship(
        back_populates="topics",
    )

    learning_content: Mapped["LearningContent | None"] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
        uselist=False,
    )


class LearningContent(Base):

    __tablename__ = "learning_contents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
        unique=True,
    )

    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    topic: Mapped["Topic"] = relationship(
        back_populates="learning_content",
    )

class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    journey_id: Mapped[int] = mapped_column(
        ForeignKey("journeys.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    journey: Mapped["Journey"] = relationship(
        back_populates="assessments",
    )

    questions: Mapped[list["AssessmentQuestion"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="AssessmentQuestion.order",
    )

    covered_through_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id"),
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    options: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    correct_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    assessment: Mapped["Assessment"] = relationship(
        back_populates="questions",
    )
class LearnerKnowledge(Base):
    __tablename__ = "learner_knowledge"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    journey_id: Mapped[int] = mapped_column(
        ForeignKey("journeys.id"),
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_answers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    score: Mapped[float] = mapped_column(
        default=0,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    journey: Mapped["Journey"] = relationship(
        back_populates="learner_knowledge",
    )