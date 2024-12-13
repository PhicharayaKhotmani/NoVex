#Written by Kullatida Puranaphan
#650510655
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy_serializer import SerializerMixin

from app import db

class Favorite(db.Model, SerializerMixin, UserMixin):
    __tablename__ = "favorites"
    
    serialize_rules = ("-book.favorites","-member.favorites")

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow() + timedelta(hours=7))
    deleted_at = db.Column(db.DateTime())
    deleted_by =  db.Column(db.Integer, db.ForeignKey('members.id'))
    
    member = db.relationship("Member", back_populates="favorites", foreign_keys=member_id)
    book = db.relationship("Book", back_populates="favorites", foreign_keys=book_id)
    
    def __init__(self, member_id, book_id, deleted_at=None, deleted_by=None):
        self.member_id = member_id
        self.book_id = book_id
        self.deleted_at =deleted_at
        self.deleted_by = deleted_by
    
    def update(self, member_id, book_id, deleted_at=None, deleted_by=None, updated_at=None):
        self.member_id = member_id
        self.book_id = book_id
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.updated_at = updated_at
        
    def soft_delete(self,deleter_id):
        self.deleted_by = deleter_id
        self.deleted_at = datetime.utcnow() + timedelta(hours=7)
        db.session.commit()
        
    def is_deleted(self):
        return self.deleted_at is not None