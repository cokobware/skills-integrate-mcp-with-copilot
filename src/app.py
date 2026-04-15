"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import json
import os
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


class ActivityRecord(BaseModel):
    description: str
    schedule: str
    max_participants: int


class RegistrationRecord(BaseModel):
    activity_name: str
    email: str


class ActivitiesData(BaseModel):
    activities: dict[str, ActivityRecord] = Field(default_factory=dict)
    registrations: list[RegistrationRecord] = Field(default_factory=list)


class ActivityStore:
    def __init__(self, data_file: Path):
        self._data_file = data_file
        self._lock = Lock()
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_exists()

    def get_activities(self) -> dict[str, dict[str, object]]:
        data = self._read_data()
        return self._serialize_activities(data)

    def signup(self, activity_name: str, email: str) -> None:
        with self._lock:
            data = self._read_data()
            self._validate_activity_exists(data, activity_name)

            if self._is_registered(data, activity_name, email):
                raise HTTPException(
                    status_code=400,
                    detail="Student is already signed up"
                )

            data.registrations.append(
                RegistrationRecord(activity_name=activity_name, email=email)
            )
            self._write_data(data)

    def unregister(self, activity_name: str, email: str) -> None:
        with self._lock:
            data = self._read_data()
            self._validate_activity_exists(data, activity_name)

            remaining_registrations = [
                registration for registration in data.registrations
                if not (
                    registration.activity_name == activity_name
                    and registration.email == email
                )
            ]

            if len(remaining_registrations) == len(data.registrations):
                raise HTTPException(
                    status_code=400,
                    detail="Student is not signed up for this activity"
                )

            data.registrations = remaining_registrations
            self._write_data(data)

    def _ensure_storage_exists(self) -> None:
        if self._data_file.exists():
            return

        self._write_data(self._default_data())

    def _read_data(self) -> ActivitiesData:
        with self._data_file.open("r", encoding="utf-8") as file_handle:
            raw_data = json.load(file_handle)

        return ActivitiesData.model_validate(raw_data)

    def _write_data(self, data: ActivitiesData) -> None:
        with self._data_file.open("w", encoding="utf-8") as file_handle:
            json.dump(data.model_dump(), file_handle, indent=2)
            file_handle.write("\n")

    def _serialize_activities(self, data: ActivitiesData) -> dict[str, dict[str, object]]:
        registrations_by_activity: dict[str, list[str]] = {
            activity_name: [] for activity_name in data.activities
        }

        for registration in data.registrations:
            if registration.activity_name in registrations_by_activity:
                registrations_by_activity[registration.activity_name].append(
                    registration.email
                )

        return {
            activity_name: {
                **activity.model_dump(),
                "participants": registrations_by_activity.get(activity_name, [])
            }
            for activity_name, activity in data.activities.items()
        }

    def _validate_activity_exists(self, data: ActivitiesData, activity_name: str) -> None:
        if activity_name not in data.activities:
            raise HTTPException(status_code=404, detail="Activity not found")

    def _is_registered(self, data: ActivitiesData, activity_name: str, email: str) -> bool:
        return any(
            registration.activity_name == activity_name and registration.email == email
            for registration in data.registrations
        )

    def _default_data(self) -> ActivitiesData:
        return ActivitiesData(
            activities={
                "Chess Club": ActivityRecord(
                    description="Learn strategies and compete in chess tournaments",
                    schedule="Fridays, 3:30 PM - 5:00 PM",
                    max_participants=12,
                ),
                "Programming Class": ActivityRecord(
                    description="Learn programming fundamentals and build software projects",
                    schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                    max_participants=20,
                ),
                "Gym Class": ActivityRecord(
                    description="Physical education and sports activities",
                    schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                    max_participants=30,
                ),
                "Soccer Team": ActivityRecord(
                    description="Join the school soccer team and compete in matches",
                    schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                    max_participants=22,
                ),
                "Basketball Team": ActivityRecord(
                    description="Practice and play basketball with the school team",
                    schedule="Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                    max_participants=15,
                ),
                "Art Club": ActivityRecord(
                    description="Explore your creativity through painting and drawing",
                    schedule="Thursdays, 3:30 PM - 5:00 PM",
                    max_participants=15,
                ),
                "Drama Club": ActivityRecord(
                    description="Act, direct, and produce plays and performances",
                    schedule="Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                    max_participants=20,
                ),
                "Math Club": ActivityRecord(
                    description="Solve challenging problems and participate in math competitions",
                    schedule="Tuesdays, 3:30 PM - 4:30 PM",
                    max_participants=10,
                ),
                "Debate Team": ActivityRecord(
                    description="Develop public speaking and argumentation skills",
                    schedule="Fridays, 4:00 PM - 5:30 PM",
                    max_participants=12,
                ),
            },
            registrations=[
                RegistrationRecord(activity_name="Chess Club", email="michael@mergington.edu"),
                RegistrationRecord(activity_name="Chess Club", email="daniel@mergington.edu"),
                RegistrationRecord(activity_name="Programming Class", email="emma@mergington.edu"),
                RegistrationRecord(activity_name="Programming Class", email="sophia@mergington.edu"),
                RegistrationRecord(activity_name="Gym Class", email="john@mergington.edu"),
                RegistrationRecord(activity_name="Gym Class", email="olivia@mergington.edu"),
                RegistrationRecord(activity_name="Soccer Team", email="liam@mergington.edu"),
                RegistrationRecord(activity_name="Soccer Team", email="noah@mergington.edu"),
                RegistrationRecord(activity_name="Basketball Team", email="ava@mergington.edu"),
                RegistrationRecord(activity_name="Basketball Team", email="mia@mergington.edu"),
                RegistrationRecord(activity_name="Art Club", email="amelia@mergington.edu"),
                RegistrationRecord(activity_name="Art Club", email="harper@mergington.edu"),
                RegistrationRecord(activity_name="Drama Club", email="ella@mergington.edu"),
                RegistrationRecord(activity_name="Drama Club", email="scarlett@mergington.edu"),
                RegistrationRecord(activity_name="Math Club", email="james@mergington.edu"),
                RegistrationRecord(activity_name="Math Club", email="benjamin@mergington.edu"),
                RegistrationRecord(activity_name="Debate Team", email="charlotte@mergington.edu"),
                RegistrationRecord(activity_name="Debate Team", email="henry@mergington.edu"),
            ],
        )


store = ActivityStore(current_dir / "data" / "activities.json")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return store.get_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    store.signup(activity_name, email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    store.unregister(activity_name, email)
    return {"message": f"Unregistered {email} from {activity_name}"}
