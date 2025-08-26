from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import User, Note
from app.schemas import UserCreate, UserUpdate, NoteCreate, NoteUpdate
from app.auth import get_password_hash, verify_password
from typing import List, Optional


# User CRUD operations
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    # Check for existing user with same email or username
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed due to constraint violation"
        )


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Check for unique constraints
    if "email" in update_data:
        existing_user = get_user_by_email(db, update_data["email"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if "username" in update_data:
        existing_user = get_user_by_username(db, update_data["username"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    try:
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User update failed due to constraint violation"
        )


# Note CRUD operations
def get_note(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    return db.query(Note).filter(
        Note.id == note_id,
        Note.owner_id == user_id
    ).first()


def get_public_note(db: Session, note_id: int) -> Optional[Note]:
    return db.query(Note).filter(
        Note.id == note_id,
        Note.is_public == True
    ).first()


def get_user_notes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    return db.query(Note).filter(Note.owner_id == user_id).offset(skip).limit(limit).all()


def get_public_notes(db: Session, skip: int = 0, limit: int = 100) -> List[Note]:
    return db.query(Note).filter(Note.is_public == True).offset(skip).limit(limit).all()


def create_note(db: Session, note: NoteCreate, user_id: int) -> Note:
    db_note = Note(**note.dict(), owner_id=user_id)
    
    try:
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note creation failed"
        )


def update_note(db: Session, note_id: int, note_update: NoteUpdate, user_id: int) -> Note:
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    update_data = note_update.dict(exclude_unset=True)
    
    try:
        for field, value in update_data.items():
            setattr(db_note, field, value)
        db.commit()
        db.refresh(db_note)
        return db_note
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note update failed"
        )


def delete_note(db: Session, note_id: int, user_id: int) -> bool:
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    try:
        db.delete(db_note)
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note deletion failed"
        )
