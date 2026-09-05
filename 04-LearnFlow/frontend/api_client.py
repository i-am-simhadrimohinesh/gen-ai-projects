import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL")


# --------------------------------------------------
# Journeys
# --------------------------------------------------

def get_journeys():
    response = requests.get(
        f"{BACKEND_URL}/journeys",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_journey(journey_id: int):
    response = requests.get(
        f"{BACKEND_URL}/journeys/{journey_id}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def create_journey(
    title: str,
    reason: str,
    goal: str,
    existing_knowledge: str,
    requested_topics: list[str],
):
    response = requests.post(
        f"{BACKEND_URL}/journeys",
        json={
            "title": title,
            "reason": reason,
            "goal": goal,
            "existing_knowledge": existing_knowledge,
            "requested_topics": requested_topics,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# Topics / Learning
# --------------------------------------------------

def get_topic_notes(topic_id: int):
    response = requests.get(
        f"{BACKEND_URL}/topics/{topic_id}/notes",
        timeout=120,
    )

    response.raise_for_status()

    return response.json()

def complete_topic(topic_id: int):
    response = requests.post(
        f"{BACKEND_URL}/topics/{topic_id}/complete",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# Assessments

def get_assessment_history(journey_id: int):
    response = requests.get(
        f"{BACKEND_URL}/assessments/journeys/{journey_id}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def create_assessment(journey_id: int):
    response = requests.post(
        f"{BACKEND_URL}/assessments/journeys/{journey_id}",
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def get_assessment(assessment_id: int):
    response = requests.get(
        f"{BACKEND_URL}/assessments/{assessment_id}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def submit_assessment(assessment_id: int, answers: list[dict]):
    response = requests.post(
        f"{BACKEND_URL}/assessments/{assessment_id}/submit",
        json={"answers": answers},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
def delete_journey(journey_id: int):
    response = requests.delete(
        f"{BACKEND_URL}/journeys/{journey_id}"
    )

    response.raise_for_status()

    return response.json()