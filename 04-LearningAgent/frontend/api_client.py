import requests


API_BASE_URL = "http://127.0.0.1:8000"


def get_journeys():
    response = requests.get(
        f"{API_BASE_URL}/journeys",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_journey(journey_id: int):
    response = requests.get(
        f"{API_BASE_URL}/journeys/{journey_id}",
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
        f"{API_BASE_URL}/journeys",
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
def get_topic_notes(topic_id: int):
    response = requests.get(
        f"{API_BASE_URL}/topics/{topic_id}/notes",
        timeout=120,
    )
    response.raise_for_status()
    return response.json()
def download_topic_notes(topic_id: int):
    response = requests.get(
        f"{API_BASE_URL}/topics/{topic_id}/notes/download",
        timeout=30,
    )
    response.raise_for_status()
    return response.content, response.headers.get(
        "content-disposition",
        "",
    )


def complete_topic(topic_id: int):
    response = requests.post(
        f"{API_BASE_URL}/topics/{topic_id}/complete",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
def get_assessment(journey_id: int):
    response = requests.get(
        f"{API_BASE_URL}/assessments/journeys/{journey_id}",
        timeout=120,
    )
    response.raise_for_status()

    return response.json()

def submit_assessment(
    assessment_id: int,
    answers: list[dict],
):
    response = requests.post(
        f"{API_BASE_URL}/assessments/{assessment_id}/submit",
        json={
            "answers": answers,
        },
        timeout=30,
    )
    response.raise_for_status()

    return response.json()