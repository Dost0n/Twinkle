from fastapi import APIRouter, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from db.session import get_db
from db.models import Post
from schemas.users import UserShow
from core.security import get_current_user
import os
from schemas.posts import PostCreateSchema, PostShowSchema
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional

router = APIRouter()

def save_uploaded_file(file: UploadFile):
    file_path = os.path.join("uploaded_files", file.filename)
    with open(file_path, "ab") as buffer:
        buffer.write(file.file.read())
    return file_path


def get_file_type(filename: str):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return "image"
    elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        return "video"
    else:
        return "unknown"


def delete_file_from_disk(file_path: str):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="O'chirilishi kerak bo'lgan fayl topilmadi!")


@router.post("/create", response_model=PostShowSchema)
async def create_post(file: UploadFile = File(...), caption: str = Form(...), db: Session = Depends(get_db)):
    saved_file_path = save_uploaded_file(file)
    file_type = get_file_type(file.filename)
    new_post = Post(user_id=1, caption=caption, file_url=saved_file_path, file_type=file_type)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/all", response_model=List[PostShowSchema])
def get_posts(db: Session = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    posts = db.query(Post).all()[skip: skip + limit]
    total_posts = len(db.query(Post).all())
    if skip >= total_posts:
        raise HTTPException(status_code=400, detail="Skip value is too large")
    return posts


@router.get("/{id}/get", response_model=PostShowSchema)
def get_post(id:int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == id).first()
    if not db_post:
        raise HTTPException(status_code=400, detail="This post not found")
    if db_post.file_type == "image":
        media_type = "image/jpeg" if db_post.file_url.endswith(('.jpg', '.jpeg')) else "image/png"
    elif db_post.file_type == "video":
        media_type = "video/mp4"
    else:
        return JSONResponse(status_code=400, content={"message": "Noto'g'ri fayl turi!"})
    return FileResponse(db_post.file_url, media_type=media_type)


@router.patch("/{id}/update", response_model=PostShowSchema)
def update_post(id:int, file: UploadFile = File(...), caption: str = Form(...), db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == id).first()
    if not db_post:
        raise HTTPException(status_code=400, detail="This post not found")
    if file:
        db_post.file_url=save_uploaded_file(file)
        db_post.file_type=get_file_type(file.filename)
    if caption:
        db_post.caption = caption
    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("{id}/delete")
def delete_post(id:int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == id).first()
    if not db_post:
        raise HTTPException(status_code=400, detail="This post not found")
    delete_file_from_disk(db_post.file_url)
    db.delete(db_post)
    db.commit()
    return {"message": "Fayl muvaffaqiyatli o'chirildi!"}