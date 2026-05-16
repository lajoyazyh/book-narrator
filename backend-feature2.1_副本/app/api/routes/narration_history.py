from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.narration_task import NarrationTask
from app.schemas.narration_task import NarrationTaskUpdate


router = APIRouter(prefix="/narration-history", tags=["narration-history"])


def task_to_dict(task: NarrationTask) -> dict:
    return {
        "task_id": task.task_id,
        "book_id": task.book_id,
        "book_title": task.book_title,
        "filename": task.filename,
        "mode": task.mode,
        "style": task.style,
        "voice": task.voice,
        "start_page": task.start_page,
        "end_page": task.end_page,
        "chapter_number": task.chapter_number,
        "task_instruction": task.task_instruction,
        "custom_text": task.custom_text,
        "script": task.script,
        "audio_urls": task.get_audio_urls(),
        "status": task.status,
        "error_message": task.error_message,
        "remark": task.remark,
        "favorite": task.favorite,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


@router.get("")
def list_history(
        keyword: str | None = None,
        book_id: str | None = None,
        db: Session = Depends(get_db),
):
    query = db.query(NarrationTask)

    if book_id:
        query = query.filter(NarrationTask.book_id == book_id)

    if keyword:
        like_value = f"%{keyword}%"
        query = query.filter(
            (NarrationTask.book_title.like(like_value))
            | (NarrationTask.filename.like(like_value))
            | (NarrationTask.task_instruction.like(like_value))
            | (NarrationTask.script.like(like_value))
        )

    tasks = query.order_by(NarrationTask.id.desc()).all()

    return {
        "code": 0,
        "message": "success",
        "data": [task_to_dict(task) for task in tasks],
    }


@router.get("/{task_id}")
def get_history_detail(task_id: str, db: Session = Depends(get_db)):
    task = db.query(NarrationTask).filter(NarrationTask.task_id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="历史解说记录不存在")

    return {
        "code": 0,
        "message": "success",
        "data": task_to_dict(task),
    }


@router.put("/{task_id}")
def update_history(
        task_id: str,
        payload: NarrationTaskUpdate,
        db: Session = Depends(get_db),
):
    task = db.query(NarrationTask).filter(NarrationTask.task_id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="历史解说记录不存在")

    if payload.remark is not None:
        task.remark = payload.remark

    if payload.favorite is not None:
        task.favorite = payload.favorite

    db.commit()
    db.refresh(task)

    return {
        "code": 0,
        "message": "success",
        "data": task_to_dict(task),
    }


@router.delete("/{task_id}")
def delete_history(task_id: str, db: Session = Depends(get_db)):
    task = db.query(NarrationTask).filter(NarrationTask.task_id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="历史解说记录不存在")

    db.delete(task)
    db.commit()

    return {
        "code": 0,
        "message": "success",
        "data": True,
    }