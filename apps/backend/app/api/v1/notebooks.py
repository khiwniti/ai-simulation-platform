"""
Notebook API endpoints.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.notebook import notebook
from app.crud.workbook import workbook as workbook_crud
from app.schemas.notebook import NotebookCreate, NotebookUpdate, NotebookResponse, NotebookAutoSave, NotebookExport, NotebookImport
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter()


@router.get("/", response_model=List[NotebookResponse])
def read_notebooks(
    workbook_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[NotebookResponse]:
    """
    Retrieve notebooks with optional workbook filtering.
    """
    if workbook_id:
        # Verify workbook exists
        db_workbook = workbook_crud.get(db, id=workbook_id)
        if not db_workbook:
            raise NotFoundError(detail=f"Workbook with id {workbook_id} not found")
        
        notebooks = notebook.get_by_workbook(db, workbook_id=workbook_id, skip=skip, limit=limit)
    else:
        notebooks = notebook.get_multi(db, skip=skip, limit=limit)
    
    return notebooks


@router.post("/", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
def create_notebook(
    notebook_in: NotebookCreate,
    db: Session = Depends(get_db)
) -> NotebookResponse:
    """
    Create new notebook.
    """
    # Verify workbook exists
    db_workbook = workbook_crud.get(db, id=notebook_in.workbook_id)
    if not db_workbook:
        raise NotFoundError(detail=f"Workbook with id {notebook_in.workbook_id} not found")
    
    # Check if notebook with same title already exists in workbook
    existing_notebook = notebook.get_by_title_and_workbook(
        db, title=notebook_in.title, workbook_id=notebook_in.workbook_id
    )
    if existing_notebook:
        raise ConflictError(
            detail=f"Notebook with title '{notebook_in.title}' already exists in this workbook"
        )
    
    created_notebook = notebook.create(db, obj_in=notebook_in)
    return created_notebook


@router.get("/{notebook_id}", response_model=NotebookResponse)
def read_notebook(
    notebook_id: UUID,
    include_cells: bool = True,
    db: Session = Depends(get_db)
) -> NotebookResponse:
    """
    Get notebook by ID with optional cell inclusion.
    """
    if include_cells:
        db_notebook = notebook.get_with_cells(db, id=notebook_id)
    else:
        db_notebook = notebook.get(db, id=notebook_id)
    
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    return db_notebook


@router.put("/{notebook_id}", response_model=NotebookResponse)
def update_notebook(
    notebook_id: UUID,
    notebook_in: NotebookUpdate,
    db: Session = Depends(get_db)
) -> NotebookResponse:
    """
    Update notebook.
    """
    db_notebook = notebook.get(db, id=notebook_id)
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    # Check for title conflicts if title is being updated
    if notebook_in.title and notebook_in.title != db_notebook.title:
        existing_notebook = notebook.get_by_title_and_workbook(
            db, title=notebook_in.title, workbook_id=db_notebook.workbook_id
        )
        if existing_notebook:
            raise ConflictError(
                detail=f"Notebook with title '{notebook_in.title}' already exists in this workbook"
            )
    
    updated_notebook = notebook.update(db, db_obj=db_notebook, obj_in=notebook_in)
    
    # Increment version if content changed
    if notebook_in.title or notebook_in.metadata:
        notebook.increment_version(db, notebook_id)
    
    return updated_notebook


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notebook(
    notebook_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete notebook.
    """
    db_notebook = notebook.get(db, id=notebook_id)
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    notebook.remove(db, id=notebook_id)


@router.post("/{notebook_id}/auto-save", response_model=NotebookResponse)
def auto_save_notebook(
    notebook_id: UUID,
    auto_save_data: NotebookAutoSave,
    db: Session = Depends(get_db)
) -> NotebookResponse:
    """
    Auto-save notebook changes without incrementing version.
    """
    from app.services.notebook_persistence import notebook_persistence_service
    
    db_notebook = notebook.get(db, id=notebook_id)
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    saved_notebook = notebook_persistence_service.auto_save(
        db=db,
        notebook_id=notebook_id,
        auto_save_data=auto_save_data
    )
    
    return saved_notebook


@router.post("/{notebook_id}/export", response_model=dict)
def export_notebook(
    notebook_id: UUID,
    export_format: str = "jupyter",
    db: Session = Depends(get_db)
) -> dict:
    """
    Export notebook to various formats (Jupyter .ipynb, JSON, etc.).
    """
    from app.services.notebook_io import notebook_io_service
    
    db_notebook = notebook.get_with_cells(db, id=notebook_id)
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    exported_data = notebook_io_service.export_notebook(
        notebook=db_notebook,
        format=export_format
    )
    
    return exported_data


@router.post("/import", response_model=NotebookResponse)
def import_notebook(
    import_data: NotebookImport,
    workbook_id: UUID,
    db: Session = Depends(get_db)
) -> NotebookResponse:
    """
    Import notebook from various formats (Jupyter .ipynb, JSON, etc.).
    """
    from app.services.notebook_io import notebook_io_service
    
    # Verify workbook exists
    db_workbook = workbook_crud.get(db, id=workbook_id)
    if not db_workbook:
        raise NotFoundError(detail=f"Workbook with id {workbook_id} not found")
    
    imported_notebook = notebook_io_service.import_notebook(
        db=db,
        import_data=import_data,
        workbook_id=workbook_id
    )
    
    return imported_notebook


@router.get("/{notebook_id}/versions", response_model=List[dict])
def get_notebook_versions(
    notebook_id: UUID,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get version history for a notebook.
    """
    from app.services.notebook_versioning import notebook_versioning_service
    
    db_notebook = notebook.get(db, id=notebook_id)
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    versions = notebook_versioning_service.get_version_history(
        db=db,
        notebook_id=notebook_id,
        limit=limit
    )
    
    return versions


@router.post("/{notebook_id}/versions", response_model=dict)
def create_notebook_version(
    notebook_id: UUID,
    version_message: str = "",
    db: Session = Depends(get_db)
) -> dict:
    """
    Create a new version checkpoint for the notebook.
    """
    from app.services.notebook_versioning import notebook_versioning_service
    
    db_notebook = notebook.get_with_cells(db, id=notebook_id)
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    version = notebook_versioning_service.create_version(
        db=db,
        notebook=db_notebook,
        message=version_message
    )
    
    return version


@router.post("/{notebook_id}/backup", response_model=dict)
def backup_notebook(
    notebook_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """
    Create a backup of the notebook.
    """
    from app.services.notebook_backup import notebook_backup_service
    
    db_notebook = notebook.get_with_cells(db, id=notebook_id)
    if not db_notebook:
        raise NotFoundError(detail=f"Notebook with id {notebook_id} not found")
    
    backup_info = notebook_backup_service.create_backup(
        db=db,
        notebook=db_notebook
    )
    
    return backup_info


@router.post("/{notebook_id}/restore", response_model=NotebookResponse)
def restore_notebook(
    notebook_id: UUID,
    backup_id: str,
    db: Session = Depends(get_db)
) -> NotebookResponse:
    """
    Restore notebook from a backup.
    """
    from app.services.notebook_backup import notebook_backup_service
    
    restored_notebook = notebook_backup_service.restore_backup(
        db=db,
        notebook_id=notebook_id,
        backup_id=backup_id
    )
    
    if not restored_notebook:
        raise NotFoundError(detail=f"Backup {backup_id} not found or restore failed")
    
    return restored_notebook