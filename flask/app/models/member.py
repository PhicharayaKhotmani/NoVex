#Written by Kullatida Puranaphan
#650510655
from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .book import Book
from sqlalchemy.orm import relationship
class Member(db.Model, UserMixin,SerializerMixin):
    __tablename__ = "members"
    
    serialize_rules = ("-books.member", "-favorites.member")

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    image_url = db.Column(db.String())
    birthday = db.Column(db.Date())
    is_writer = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    deleted_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow() + timedelta(hours=7))
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow() + timedelta(hours=7))
    
    books = db.relationship("Book", back_populates="member", foreign_keys="Book.member_id")
    favorites = db.relationship("Favorite", back_populates="member", foreign_keys="Favorite.member_id")
    # books = db.relationship("Book", backref="member",  foreign_keys="Book.member_id")
    # favorites = db.relationship("Favorite", backref="member",  foreign_keys="Favorite.member_id")
    
    def __init__(self, username, email, password, image_url, birthday, is_writer, is_admin, deleted_at=None):
        self.username = username
        self.email = email
        self.password = password
        self.image_url = image_url
        self.birthday = birthday
        self.is_writer = is_writer
        self.is_admin = is_admin
        self.deleted_at = deleted_at
        
    def soft_delete(self):
        self.deleted_at = datetime.utcnow() + timedelta(hours=7)

    def is_deleted(self):
        return self.deleted_at is not None
        
    def update(self, username, email, password, image_url, birthday, is_writer=False, is_admin= False, deleted_at=None, updated_at=None):
        self.username = username
        self.email = email
        self.password = password
        self.image_url = image_url
        self.birthday = birthday
        self.is_writer = is_writer
        self.is_admin = is_admin
        self.deleted_at = deleted_at
        self.updated_at = updated_at 
    
    def is_adult(self):
        today = datetime.today()
        eighteen_years_ago = today - timedelta(days=365 * 18)
        return self.birthday <= eighteen_years_ago