from sqlalchemy.orm import Session

from app.db.models import (
    Assessment as AssessmentModel,
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
        covered_through_order: int,
    ) -> AssessmentModel:

        db_assessment = AssessmentModel(
        journey_id=journey_id,
        covered_through_order=covered_through_order,
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


    def generate_assessment(self, journey_id: int) -> AssessmentModel:
        learning_service = LearningService(self.db)

        assessment_context = learning_service.get_assessment_context(
            journey_id
        )
        covered_topics = assessment_context["covered_topics"]

        covered_through_order = max(
            topic["order"]
            for topic in covered_topics
        )
        llm = get_llm()

        graph = build_assessment_generator_graph(llm)

        result = graph.invoke(
            {
                "journey_id": journey_id,
                "journey": assessment_context["journey"],
                "covered_topics": assessment_context["covered_topics"],
                "weak_topics": assessment_context.get("weak_topics", []),
                "assessment_context": assessment_context,
            }
        )

        validation_errors = result.get("validation_errors", [])

        if validation_errors:
            raise ValueError(
                "Assessment generation failed: "
                + "; ".join(validation_errors)
            )

        questions = result.get("questions", [])

        if len(questions) != 10:
            raise ValueError(
                f"Expected 10 questions, but received {len(questions)}."
            )

        assessment = Assessment(
            questions=questions
        )

        return self.save_assessment(
            journey_id=journey_id,
            assessment=assessment,
            covered_through_order=covered_through_order,
        )
    def get_or_generate_assessment(
        self,
        journey_id: int,
    ) -> AssessmentModel:

        learning_service = LearningService(self.db)

        assessment_context = learning_service.get_assessment_context(
            journey_id
        )

        covered_topics = assessment_context["covered_topics"]

        if not covered_topics:
            raise ValueError(
                "No completed topics available for assessment."
            )

        current_covered_through_order = max(
            topic["order"]
            for topic in covered_topics
        )

        existing_assessment = (
            self.db.query(AssessmentModel)
            .filter(
                AssessmentModel.journey_id == journey_id,
                AssessmentModel.covered_through_order
                == current_covered_through_order,
            )
            .order_by(AssessmentModel.created_at.desc())
            .first()
        )

        if existing_assessment is not None:
            return existing_assessment

        return self.generate_assessment(
            journey_id=journey_id,
        )
    def evaluate_assessment(
        self,
        assessment_id: int,
        submission: AssessmentSubmission,
    ) -> AssessmentResult:

        assessment = (
            self.db.query(AssessmentModel)
            .filter(
                AssessmentModel.id == assessment_id,
            )
            .first()
        )

        if assessment is None:
            raise ValueError("Assessment not found.")

        question_map = {
            question.id: question
            for question in assessment.questions
        }

        submitted_question_ids = {
            answer.question_id
            for answer in submission.answers
        }

        unknown_question_ids = (
            submitted_question_ids - question_map.keys()
        )

        if unknown_question_ids:
            raise ValueError(
                "Submission contains invalid question IDs."
            )

        correct_answers = 0
        question_results = []

        for answer in submission.answers:
            question = question_map[answer.question_id]

            is_correct = (
                answer.selected_answer == question.correct_answer
            )

            if is_correct:
                correct_answers += 1

            question_results.append(
                {
                    "question_id": question.id,
                    "topic": question.topic,
                    "correct": is_correct,
                }
            )

        total_questions = len(assessment.questions)
        answered_questions = len(submission.answers)

        score = (
            correct_answers / total_questions * 100
            if total_questions
            else 0
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
            question_results=question_results,
        )
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
                    LearnerKnowledge.journey_id == journey_id,
                    LearnerKnowledge.topic == topic,
                )
                .first()
            )

            if knowledge is None:
                knowledge = LearnerKnowledge(
                    journey_id=journey_id,
                    topic=topic,
                )
                self.db.add(knowledge)

            knowledge.attempts = (knowledge.attempts or 0) + 1
            knowledge.correct_answers = (
                (knowledge.correct_answers or 0)
                + stats["correct"]
            )
            knowledge.total_answers = (
                (knowledge.total_answers or 0)
                + stats["total"]
            )

            knowledge.score = (
                knowledge.correct_answers
                / knowledge.total_answers
                * 100
            )

        self.db.commit()