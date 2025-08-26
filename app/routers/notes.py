from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_active_user
from app.crud import (
    get_note, get_public_note, get_user_notes, get_public_notes,
    create_note, update_note, delete_note
)
from app.schemas import Note, NoteCreate, NoteUpdate, Message
from app.models import User

router = APIRouter()


@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_user_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new note for the authenticated user.
    
    The note will be associated with the current user's account.
    """
    return create_note(db=db, note=note, user_id=current_user.id)


@router.get("/", response_model=List[Note])
def read_user_notes(
    skip: int = Query(0, ge=0, description="Number of notes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of notes to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all notes for the authenticated user.
    
    Supports pagination with skip and limit parameters.
    """
    notes = get_user_notes(db, user_id=current_user.id, skip=skip, limit=limit)
    return notes


@router.get("/public", response_model=List[Note])
def read_public_notes(
    skip: int = Query(0, ge=0, description="Number of notes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of notes to return"),
    db: Session = Depends(get_db)
):
    """
    Get all public notes.
    
    This endpoint doesn't require authentication and returns notes
    that have been marked as public by their owners.
    """
    notes = get_public_notes(db, skip=skip, limit=limit)
    return notes


@router.get("/{note_id}", response_model=Note)
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific note by ID.
    
    Users can only access their own notes or public notes.
    """
    # First try to get user's own note
    note = get_note(db, note_id=note_id, user_id=current_user.id)
    if note:
        return note
    
    # If not found, try to get public note
    note = get_public_note(db, note_id=note_id)
    if note:
        return note
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Note not found"
    )


@router.put("/{note_id}", response_model=Note)
def update_user_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a specific note.
    
    Users can only update their own notes. The operation is idempotent -
    multiple identical requests will produce the same result.
    """
    return update_note(db=db, note_id=note_id, note_update=note_update, user_id=current_user.id)


@router.delete("/{note_id}", response_model=Message)
def delete_user_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a specific note.
    
    Users can only delete their own notes. The operation is idempotent -
    attempting to delete a non-existent note will return a 404 error.
    """
    delete_note(db=db, note_id=note_id, user_id=current_user.id)
    return {"message": "Note deleted successfully"}
