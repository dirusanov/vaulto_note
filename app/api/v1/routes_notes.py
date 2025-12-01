from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.api import deps
from app.models.user import User
from app.models.note import Note
from app.schemas.note import Note as NoteSchema, NoteCreate, NoteUpdate

router = APIRouter()

@router.get("/", response_model=List[NoteSchema])
async def read_notes(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve notes.
    """
    result = await db.execute(
        select(Note).where(Note.user_id == current_user.id).offset(skip).limit(limit)
    )
    notes = result.scalars().all()
    return notes

@router.post("/", response_model=NoteSchema)
async def create_note(
    *,
    db: AsyncSession = Depends(deps.get_db),
    note_in: NoteCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new note.
    """
    note = Note(
        **note_in.model_dump(),
        user_id=current_user.id,
        title=None,  # Explicitly set to None since we're using encrypted fields
        content=None  # Explicitly set to None since we're using encrypted fields
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

@router.get("/{note_id}", response_model=NoteSchema)
async def read_note(
    *,
    db: AsyncSession = Depends(deps.get_db),
    note_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get note by ID.
    """
    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteSchema)
async def update_note(
    *,
    db: AsyncSession = Depends(deps.get_db),
    note_id: uuid.UUID,
    note_in: NoteUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update note.
    """
    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
        
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

@router.delete("/{note_id}", response_model=NoteSchema)
async def delete_note(
    *,
    db: AsyncSession = Depends(deps.get_db),
    note_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete note.
    """
    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    await db.delete(note)
    await db.commit()
    return note
