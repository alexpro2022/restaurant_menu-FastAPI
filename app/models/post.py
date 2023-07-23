from datetime import datetime as dt

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, orm

from app.core import Base


class Post(Base):
    title = Column(String(100), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=dt.now)
    updated = Column(DateTime)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    author = orm.relationship('User', lazy='joined')

    def __repr__(self) -> str:
        return (
            f'\ntitle: {self.title},'
            f'\ncontent: {self.content[:100]},'
            f'\ncreated: {self.created},'
            f'\nupdated: {self.updated},'
            f'\nlikes: {self.likes},'
            f'\ndislikes: {self.dislikes},'
            f'\nauthor: {self.author}.\n'
        )
