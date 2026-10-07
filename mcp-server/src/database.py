import os
import json
from typing import Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(override=True)

DATABASE_URL = os.environ["DATABASE_URL"]

print("DATABASE_URL =", os.getenv("DATABASE_URL"))

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def get_user_preferences(user_id: str) -> dict[str, Any] | None:
    query = text("""
        SELECT
            user_id,
            email,
            created_at,
            last_active_at,
            app_language,
            preferred_duration_minutes,
            primary_meditation_category,
            physical_condition,
            mental_condition,
            computed_behavior_metrics
        FROM user_behavior_profiles
        WHERE user_id = :user_id
    """)

    with engine.connect() as connection:
        row = (
            connection.execute(
                query,
                {"user_id": user_id},
            )
            .mappings()
            .first()
        )

        if row is None:
            return None

        return dict(row)


def update_user_preferences(
    user_id: str,
    app_language: str | None = None,
    preferred_duration_minutes: int | None = None,
    primary_meditation_category: str | None = None,
    physical_condition: dict | None = None,
    mental_condition: dict | None = None,
) -> dict[str, Any] | None:

    updates = {}
    set_clauses = []

    if app_language is not None:
        set_clauses.append("app_language = :app_language")
        updates["app_language"] = app_language

    if preferred_duration_minutes is not None:
        set_clauses.append("preferred_duration_minutes = :preferred_duration_minutes")
        updates["preferred_duration_minutes"] = preferred_duration_minutes

    if primary_meditation_category is not None:
        set_clauses.append("primary_meditation_category = :primary_meditation_category")
        updates["primary_meditation_category"] = primary_meditation_category

    if physical_condition is not None:
        set_clauses.append(
            "physical_condition = "
            "physical_condition || CAST(:physical_condition AS jsonb)"
        )
        updates["physical_condition"] = json.dumps(physical_condition)

    if mental_condition is not None:
        set_clauses.append(
            "mental_condition = " "mental_condition || CAST(:mental_condition AS jsonb)"
        )
        updates["mental_condition"] = json.dumps(mental_condition)

    if not set_clauses:
        return get_user_preferences(user_id)

    updates["user_id"] = user_id

    query = text(f"""
        UPDATE user_behavior_profiles
        SET
            {", ".join(set_clauses)},
            last_active_at = CURRENT_TIMESTAMP
        WHERE user_id = :user_id
    """)

    with engine.begin() as connection:
        result = connection.execute(query, updates)

        if result.rowcount == 0:
            return None

    return get_user_preferences(user_id)


def search_users(
    email: str | None = None,
    app_language: str | None = None,
    primary_meditation_category: str | None = None,
) -> list[dict[str, Any]]:

    conditions = []
    parameters = {}

    if email:
        conditions.append("email ILIKE :email")
        parameters["email"] = f"%{email}%"

    if app_language:
        conditions.append("app_language = :app_language")
        parameters["app_language"] = app_language

    if primary_meditation_category:
        conditions.append(
            "primary_meditation_category = " ":primary_meditation_category"
        )
        parameters["primary_meditation_category"] = primary_meditation_category

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = text(f"""
        SELECT
            user_id,
            email,
            app_language,
            preferred_duration_minutes,
            primary_meditation_category,
            last_active_at
        FROM user_behavior_profiles
        {where_clause}
        ORDER BY last_active_at DESC
        LIMIT 50
    """)

    with engine.connect() as connection:
        rows = (
            connection.execute(
                query,
                parameters,
            )
            .mappings()
            .all()
        )

        return [dict(row) for row in rows]


def get_user_behavior(
    user_id: str,
) -> dict[str, Any] | None:

    query = text("""
        SELECT
            user_id,
            computed_behavior_metrics,
            last_active_at
        FROM user_behavior_profiles
        WHERE user_id = :user_id
    """)

    with engine.connect() as connection:
        row = (
            connection.execute(
                query,
                {"user_id": user_id},
            )
            .mappings()
            .first()
        )

        if row is None:
            return None

        return dict(row)
