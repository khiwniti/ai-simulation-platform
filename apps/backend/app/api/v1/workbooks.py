"""
Workbook API endpoints.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.workbook import workbook
from app.schemas.workbook import WorkbookCreate, WorkbookUpdate, WorkbookResponse
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter()


@router.get("/", response_model=List[WorkbookResponse])
def read_workbooks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[WorkbookResponse]:
    """
    Retrieve workbooks with pagination.
    """
    workbooks = workbook.get_multi_with_notebook_count(db, skip=skip, limit=limit)
    return workbooks


@router.post("/", response_model=WorkbookResponse, status_code=status.HTTP_201_CREATED)
def create_workbook(
    workbook_in: WorkbookCreate,
    db: Session = Depends(get_db)
) -> WorkbookResponse:
    """
    Create new workbook.
    """
    # Check if workbook with same title already exists
    existing_workbook = workbook.get_by_title(db, title=workbook_in.title)
    if existing_workbook:
        raise ConflictError(detail=f"Workbook with title '{workbook_in.title}' already exists")
    
    created_workbook = workbook.create(db, obj_in=workbook_in)
    return created_workbook


@router.get("/{workbook_id}", response_model=WorkbookResponse)
def read_workbook(
    workbook_id: UUID,
    db: Session = Depends(get_db)
) -> WorkbookResponse:
    """
    Get workbook by ID.
    """
    db_workbook = workbook.get_with_notebook_count(db, id=workbook_id)
    if not db_workbook:
        raise NotFoundError(detail=f"Workbook with id {workbook_id} not found")
    return db_workbook


@router.put("/{workbook_id}", response_model=WorkbookResponse)
def update_workbook(
    workbook_id: UUID,
    workbook_in: WorkbookUpdate,
    db: Session = Depends(get_db)
) -> WorkbookResponse:
    """
    Update workbook.
    """
    db_workbook = workbook.get(db, id=workbook_id)
    if not db_workbook:
        raise NotFoundError(detail=f"Workbook with id {workbook_id} not found")
    
    # Check for title conflicts if title is being updated
    if workbook_in.title and workbook_in.title != db_workbook.title:
        existing_workbook = workbook.get_by_title(db, title=workbook_in.title)
        if existing_workbook:
            raise ConflictError(detail=f"Workbook with title '{workbook_in.title}' already exists")
    
    updated_workbook = workbook.update(db, db_obj=db_workbook, obj_in=workbook_in)
    return updated_workbook


@router.delete("/{workbook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workbook(
    workbook_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete workbook.
    """
    db_workbook = workbook.get(db, id=workbook_id)
    if not db_workbook:
        raise NotFoundError(detail=f"Workbook with id {workbook_id} not found")
    
    workbook.remove(db, id=workbook_id)