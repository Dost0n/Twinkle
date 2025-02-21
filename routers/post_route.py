from fastapi import APIRouter, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from db.session import get_db
from db.models import Post, PostLike, Comment, PostDislike, CommentLike, CommentDislike
from schemas.users import UserShow
from core.security import get_current_user
import os
from schemas.posts import PostShowSchema, PostLikeShowSchema, PostDislikeShowSchema, CommentCreateSchema, CommentShowSchema, CommentLikeShowSchema, CommentDislikeShowSchema
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


@router.get("/{post_id}/get", response_model=PostShowSchema)
def get_post(post_id:int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=400, detail="This post not found")
    if db_post.file_type == "image":
        media_type = "image/jpeg" if db_post.file_url.endswith(('.jpg', '.jpeg')) else "image/png"
    elif db_post.file_type == "video":
        media_type = "video/mp4"
    else:
        return JSONResponse(status_code=400, content={"message": "Noto'g'ri fayl turi!"})
    return FileResponse(db_post.file_url, media_type=media_type)


@router.patch("/{post_id}/update", response_model=PostShowSchema)
def update_post(post_id:int, file: UploadFile = File(...), caption: str = Form(...), db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
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


@router.delete("/{post_id}/delete")
def delete_post(post_id:int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=400, detail="This post not found")
    delete_file_from_disk(db_post.file_url)
    db.delete(db_post)
    db.commit()
    return {"message": "Fayl muvaffaqiyatli o'chirildi!"}


@router.post("/{post_id}/postlike")
async def create_post_like(post_id:int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post_like = db.query(PostLike).filter(PostLike.user_id == current_user.id).filter(PostLike.post_id == post_id).first()
    if db_post_like:
        db.delete(db_post_like)
        db.commit()
        return {"message": "Postdan like o'chirildi!"}
    new_post_like = PostLike(user_id=current_user.id, post_id=post_id)
    db.add(new_post_like)
    db.commit() 
    db.refresh(new_post_like)
    return {"message": "Post ga like bosildi!"}


@router.get("/{post_id}/likes", response_model=List[PostLikeShowSchema])
def get_post_likes(post_id: int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    likes = db.query(PostLike).filter(PostLike.post_id == post_id)
    return likes


@router.post("/{post_id}/postdislike")
async def create_post_dislike(post_id:int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post_dislike = db.query(PostDislike).filter(PostDislike.user_id == current_user.id).filter(PostDislike.post_id == post_id).first()
    if db_post_dislike:
        db.delete(db_post_dislike)
        db.commit()
        return {"message": "Postdan dislike o'chirildi!"}
    new_post_dislike = PostDislike(user_id=current_user.id, post_id=post_id)
    db.add(new_post_dislike)
    db.commit() 
    db.refresh(new_post_dislike)
    return {"message": "Post ga dislike bosildi!"}


@router.get("/{post_id}/dislikes", response_model=List[PostDislikeShowSchema])
def get_post_dislikes(post_id: int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    dislikes = db.query(PostDislike).filter(PostDislike.post_id == post_id)
    return dislikes


@router.post("/{post_id}/comment", response_model=CommentShowSchema)
async def create_post_comment(post_id:int, comment=CommentCreateSchema, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    new_post_comment = Comment(user_id=current_user.id, post_id=post_id, comment=comment)
    db.add(new_post_comment)
    db.commit() 
    db.refresh(new_post_comment)
    return new_post_comment


@router.get("/{post_id}/comments", response_model=List[CommentShowSchema])
def get_post_comments(post_id: int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = db.query(Comment).filter(Comment.post_id == post_id)
    return comments


@router.post("/comment/{comment_id}/like")
async def create_comment_like(comment_id:int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    db_comment_like = db.query(CommentLike).filter(CommentLike.user_id == current_user.id).filter(CommentLike.id == comment_id).first()
    if db_comment_like:
        db.delete(db_comment_like)
        db.commit()
        return {"message": "Commentdan like o'chirildi!"}
    new_comment_like = CommentLike(user_id=current_user.id, comment_id=comment_id)
    db.add(new_comment_like)
    db.commit() 
    db.refresh(new_comment_like)
    return {"message": "Commentga like bosildi!"}


@router.get("/{comment_id}/likes", response_model=List[CommentLikeShowSchema])
def get_comment_likes(comment_id: int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    likes = db.query(CommentLike).filter(CommentLike.comment_id == comment_id)
    return likes


@router.post("/comment/{comment_id}/dislike")
async def create_comment_dislike(comment_id:int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    db_comment_dislike = db.query(CommentDislike).filter(CommentDislike.user_id == current_user.id).filter(CommentDislike.id == comment_id).first()
    if db_comment_dislike:
        db.delete(db_comment_dislike)
        db.commit()
        return {"message": "Commentdan dislike o'chirildi!"}
    new_comment_dislike = CommentDislike(user_id=current_user.id, comment_id=comment_id)
    db.add(new_comment_dislike)
    db.commit() 
    db.refresh(new_comment_dislike)
    return {"message": "Commentga dislike bosildi!"}


@router.get("/{comment_id}/dislikes", response_model=List[CommentDislikeShowSchema])
def get_comment_dislikes(comment_id: int, db: Session = Depends(get_db), current_user: UserShow = Depends(get_current_user)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    dislikes = db.query(CommentDislike).filter(CommentDislike.comment_id == comment_id)
    return dislikes