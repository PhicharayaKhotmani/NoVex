#Written by Kullatida Puranaphan
#650510655

from datetime import datetime, timedelta
from sqlalchemy_serializer import SerializerMixin
from app import db
class Book(db.Model, SerializerMixin):
    __tablename__ = "books"
    
    serialize_rules = ("-member", "-genre", "-subgenre", "-chapters", "-favorites")
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    subgenre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String())
    for_adult= db.Column(db.Boolean(), default=False)
    deleted_at = db.Column(db.DateTime())
    deleted_by = db.Column(db.Integer, db.ForeignKey('members.id'))
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow() + timedelta(hours=7))
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow() + timedelta(hours=7))
    
    member = db.relationship("Member", back_populates="books", foreign_keys=member_id)
    genre = db.relationship("Genre", back_populates="book_genres", foreign_keys=genre_id)
    subgenre = db.relationship("Genre", back_populates="book_subgenres", foreign_keys=subgenre_id)
    chapters = db.relationship("Chapter", back_populates="book")
    favorites = db.relationship("Favorite", back_populates="book")
    # favorites = db.relationship("Favorite", backref="book", foreign_keys="Favorite.book_id")
    # chapters = db.relationship("Chapter", backref="book",  foreign_keys="Chapter.book_id")
    
    def __init__(self, member_id, name, description, image_url, genre_id, subgenre_id, for_adult=False, deleted_at=None, deleted_by=None):
        self.member_id = member_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.genre_id = genre_id
        self.subgenre_id = subgenre_id
        self.for_adult = for_adult
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
    
    def update(self, member_id, name, description, image_url, genre_id, subgenre_id, for_adult=False, deleted_at=None, deleted_by=None, updated_at=None):
        self.member_id = member_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.genre_id = genre_id
        self.subgenre_id = subgenre_id
        self.for_adult = for_adult
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.updated_at = updated_at
        
    def soft_delete(self,user):
        self.deleted_at = datetime.utcnow() + timedelta(hours=7)
        self.deleted_by = user
        
    def is_deleted(self):
        return self.deleted_at is not None