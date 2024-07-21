from logging import Logger

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def handle_integrity_error(logger: Logger, err: IntegrityError):
    logger.error(err)
    raise HTTPException(status_code=503, detail=f"Database error: {err}")


def handle_not_found_error(entity_name: str, entity_id: int):
    raise HTTPException(status_code=404, detail=f"{entity_name} with id {entity_id} not found.")


def handle_forbidden_error(detail: str = "Forbidden"):
    raise HTTPException(status_code=403, detail=detail)


def handle_conflict_error(detail: str):
    raise HTTPException(status_code=409, detail=detail)


def handle_bad_request_error(detail: str):
    raise HTTPException(status_code=400, detail=detail)


def handle_unprocessable_entity_error(detail: str):
    raise HTTPException(status_code=422, detail=detail)
