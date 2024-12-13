#Written by Kullatida Puranaphan
#650510655
from datetime import datetime, timedelta
from sqlalchemy_serializer import SerializerMixin

from app import db

class Chapter(db.Model, SerializerMixin):
    __tablename__ = "chapters"
    
    serialize_rules = ("-book.chapters",)
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    episode = db.Column(db.String(), nullable = False)
    title = db.Column(db.String(120), nullable = False)
    content = db.Column(db.Text, nullable = False)
    deleted_at = db.Column(db.DateTime())
    deleted_by = db.Column(db.Integer, db.ForeignKey('members.id'))
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow() + timedelta(hours=7))
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow() + timedelta(hours=7))
    
    book = db.relationship("Book", back_populates="chapters")
    
    def __init__(self, book_id, episode, titile, content, deleted_at=None, deleted_by=None):
        self.book_id = book_id
        self.episode = episode
        self.title = titile
        self.content = content
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        
    def update(self, book_id, episode, titile, content, deleted_at=None, deleted_by=None, updated_at=None):
        self.book_id = book_id
        self.episode = episode
        self.title = titile
        self.content = content
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.updated_at = updated_at
        
    def soft_delete(self):
        self.deleted_at = datetime.utcnow() + timedelta(hours=7)

    def is_deleted(self):
        return self.deleted_at is not None