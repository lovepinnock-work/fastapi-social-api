from sqlalchemy import TIMESTAMP, ForeignKey, text
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    published: Mapped[Optional[bool]] = mapped_column(server_default='TRUE', nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")
    def __repr__(self) -> str:
        return f"Post(id={self.id}, title={self.title}, content={self.content}, published={self.published}, timestamp={self.created_at})"
    
class User(Base):
    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

class Vote(Base):
    __tablename__ = "Votes"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"),
                                         primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id", ondelete="CASCADE"),
                                         primary_key=True, nullable=False)
    
class Attempts(Base):
    __tablename__ = 'login_attempts'
    user_id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    attempts: Mapped[int] = mapped_column(nullable=False)
    cooldown: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
