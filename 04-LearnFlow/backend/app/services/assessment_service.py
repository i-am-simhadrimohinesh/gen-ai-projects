from sqlalchemy.orm import Session

from app.db.models import (
    Assessment as AssessmentModel,
    AssessmentAnswer as AssessmentAnswerModel,
    AssessmentAttempt,
    AssessmentQuestion,
    LearnerKnowledge,
)

from app.services.learning_service import LearningService
from app.llm.provider import get_llm
from app.workflows.assessment_generator.graph import (
    build_assessment_generator_graph,
)
from app.workflows.assessment_generator.schemas import Assessment
from app.schemas.assessment import (
    AssessmentResult,
    AssessmentSubmission,
)


class AssessmentService:

    def __init__(self, db: Session):
        self.db = db

    def save_assessment(
        self,
        journey_id: int,
        assessment: Assessment,
    ) -> AssessmentModel:

        assessment_number = (
            self.db.query(AssessmentModel)
            .filter(
                AssessmentModel.journey_id == journey_id
            )
            .count()
            + 1
        )

        db_assessment = AssessmentModel(
            journey_id=journey_id,
            assessment_number=assessment_number,
        )

        self.db.add(db_assessment)
        self.db.flush()

        for index, question in enumerate(
            assessment.questions,
            start=1,
        ):
            db_question = AssessmentQuestion(
                assessment_id=db_assessment.id,
                question=question.question,
                options=question.options,
                correct_answer=question.correct_answer,
                topic=question.topic,
                difficulty=question.difficulty,
                order=index,
            )

            self.db.add(db_question)

        self.db.commit()
        self.db.refresh(db_assessment)

        return db_assessment

    def generate_assessment(
        self,
        journey_id: int,
    ) -> AssessmentModel:

        learning_service = LearningService(self.db)

        assessment_context = learning_service.get_assessment_context(
            journey_id
        )

        llm = get_llm()

        graph = build_assessment_generator_graph(llm)

        result = graph.invoke(
            {
                "journey_id": journey_id,
                "journey": assessment_context["journey"],
                "covered_topics": assessment_context["covered_topics"],
                "weak_topics": assessment_context.get(
                    "weak_topics",
                    [],
                ),
                "assessment_context": assessment_context,
            }
        )

        validation_errors = result.get(
            "validation_errors",
            [],
        )

        if validation_errors:
            raise ValueError(
                "Assessment generation failed: "
                + "; ".join(validation_errors)
            )

        questions = result.get(
            "questions",
            [],
        )

        if len(questions) != 10:
            raise ValueError(
                f"Expected 10 questions, but received {len(questions)}."
            )

        assessment = Assessment(
            questions=questions,
        )

        return self.save_assessment(
            journey_id=journey_id,
            assessment=assessment,
        )

    def get_assessment(
        self,
        assessment_id: int,
    ) -> AssessmentModel:

        assessment = (
            self.db.query(AssessmentModel)
            .filter(
                AssessmentModel.id == assessment_id,
            )
            .first()
        )

        if assessment is None:
            raise ValueError("Assessment not found.")

        return assessment

    def get_assessment_history(
        self,
        journey_id: int,
    ) -> list[AssessmentModel]:

        return (
            self.db.query(AssessmentModel)
            .filter(
                AssessmentModel.journey_id == journey_id,
            )
            .order_by(
                AssessmentModel.created_at.desc(),
            )
            .all()
        )

    def evaluate_assessment(
        self,
        assessment_id: int,
        submission: AssessmentSubmission,
    ) -> AssessmentResult:

        assessment = self.get_assessment(
            assessment_id,
        )

        question_map = {
            question.id: question
            for question in assessment.questions
        }

        submitted_question_ids = {
            answer.question_id
            for answer in submission.answers
        }

        unknown_question_ids = (
            submitted_question_ids
            - question_map.keys()
        )

        if unknown_question_ids:
            raise ValueError(
                "Submission contains invalid question IDs."
            )

        correct_answers = 0
        question_results = []

        for answer in submission.answers:

            question = question_map[
                answer.question_id
            ]

            is_correct = (
                answer.selected_answer
                == question.correct_answer
            )

            if is_correct:
                correct_answers += 1

            question_results.append(
                {
                    "question_id": question.id,
                    "topic": question.topic,
                    "correct": is_correct,
                    "selected_answer": answer.selected_answer,
                }
            )

        total_questions = len(
            assessment.questions
        )

        answered_questions = len(
            submission.answers
        )

        score = (
            correct_answers
            / total_questions
            * 100
            if total_questions
            else 0
        )

        attempt = self.save_attempt(
            assessment=assessment,
            submission=submission,
            question_results=question_results,
            score=score,
            total_questions=total_questions,
            answered_questions=answered_questions,
            correct_answers=correct_answers,
        )

        self.update_learner_knowledge(
            journey_id=assessment.journey_id,
            question_results=question_results,
        )

        return AssessmentResult(
            assessment_id=assessment.id,
            total_questions=total_questions,
            answered_questions=answered_questions,
            correct_answers=correct_answers,
            score=score,
            question_results=[
                {
                    "question_id": result["question_id"],
                    "topic": result["topic"],
                    "correct": result["correct"],
                }
                for result in question_results
            ],
        )

    def save_attempt(
        self,
        assessment: AssessmentModel,
        submission: AssessmentSubmission,
        question_results: list[dict],
        score: float,
        total_questions: int,
        answered_questions: int,
        correct_answers: int,
    ) -> AssessmentAttempt:

        attempt = AssessmentAttempt(
            assessment_id=assessment.id,
            score=score,
            total_questions=total_questions,
            answered_questions=answered_questions,
            correct_answers=correct_answers,
        )

        self.db.add(attempt)
        self.db.flush()

        for result in question_results:

            answer = next(
                submitted_answer
                for submitted_answer in submission.answers
                if submitted_answer.question_id
                == result["question_id"]
            )

            db_answer = AssessmentAnswerModel(
                attempt_id=attempt.id,
                question_id=result["question_id"],
                selected_answer=answer.selected_answer,
                correct=result["correct"],
            )

            self.db.add(db_answer)

        self.db.commit()
        self.db.refresh(attempt)

        return attempt

    def update_learner_knowledge(
        self,
        journey_id: int,
        question_results: list[dict],
    ) -> None:

        topic_stats: dict[str, dict[str, int]] = {}

        for result in question_results:

            topic = result["topic"]

            if topic not in topic_stats:
                topic_stats[topic] = {
                    "total": 0,
                    "correct": 0,
                }

            topic_stats[topic]["total"] += 1

            if result["correct"]:
                topic_stats[topic]["correct"] += 1

        for topic, stats in topic_stats.items():

            knowledge = (
                self.db.query(LearnerKnowledge)
                .filter(
                    LearnerKnowledge.journey_id
                    == journey_id,
                    LearnerKnowledge.topic
                    == topic,
                )
                .first()
            )

            if knowledge is None:

                knowledge = LearnerKnowledge(
                    journey_id=journey_id,
                    topic=topic,
                    attempts=0,
                    best_score=0,
                )

                self.db.add(knowledge)

            topic_score = (
                stats["correct"]
                / stats["total"]
                * 100
                if stats["total"]
                else 0
            )

            knowledge.attempts = (
                knowledge.attempts or 0
            ) + 1

            current_best = (
                knowledge.best_score or 0
            )

            if topic_score > current_best:
                knowledge.best_score = topic_score

        self.db.commit()