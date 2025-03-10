from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from db.session import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class User(BaseModel):
    __tablename__ = "users"
    username = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    email = Column(String, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    is_staff = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    auth_role = Column(String, index=True)
    auth_type = Column(String, index=True)
    auth_status = Column(String, index=True)
    password = Column(String)
    photo = Column(String, index=True)
    confirmations = relationship("Confirmation", back_populates="user")
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    postlikes = relationship("PostLike", back_populates="user")
    commentlikes = relationship("CommentLike", back_populates="user")
    postdislikes = relationship("PostDislike", back_populates="user")
    commentdislikes = relationship("CommentDislike", back_populates="user")
    profile = relationship("Profile", uselist=False, back_populates="owner")


class Profile(BaseModel):
    __tablename__ = "profiles"
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="profile")
    bio = Column(String)


class Confirmation(BaseModel):
    __tablename__ = "confirmations"
    code = Column(String)
    verify_type = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="confirmations")
    expiration_time = Column(DateTime, nullable=True)
    is_isconfirmed = Column(Boolean, default=False)


class Playlist(BaseModel):
    __tablename__ = "playlists"
    name = Column(String)
    posts = relationship("Post", back_populates="playlist")


class Post(BaseModel):
    __tablename__ = "posts"
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")
    file_url = Column(String)
    caption = Column(String)
    file_type = Column(String)
    playlist_id = Column(Integer, ForeignKey('playlists.id'))
    playlist = relationship("Playlist", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    postlikes = relationship("PostLike", back_populates="post")
    postdislikes = relationship("PostDislike", back_populates="post")


class Comment(BaseModel):
    __tablename__ = "comments"
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="comments")
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="comments")
    comment = Column(String)
    commentlikes = relationship("CommentLike", back_populates="comment")
    commentdislikes = relationship("CommentDislike", back_populates="comment")


class PostLike(BaseModel):
    __tablename__ = "postlikes"
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="postlikes")
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="postlikes")


class PostDislike(BaseModel):
    __tablename__ = "postdislikes"
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="postdislikes")
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="postdislikes")


class CommentLike(BaseModel):
    __tablename__ = "commentlikes"
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="commentlikes")
    comment_id = Column(Integer, ForeignKey('comments.id'))
    comment = relationship("Comment", back_populates="commentlikes")


class CommentDislike(BaseModel):
    __tablename__ = "commentdislikes"
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="commentdislikes")
    comment_id = Column(Integer, ForeignKey('comments.id'))
    comment = relationship("Comment", back_populates="commentdislikes")