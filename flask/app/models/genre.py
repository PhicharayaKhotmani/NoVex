#Written by Kullatida Puranaphan
#650510655
from sqlalchemy_serializer import SerializerMixin

from app import db

class Genre(db.Model, SerializerMixin):
    __tablename__ = "genres"
    
    serialize_rules = ("-book_genres", "-book_subgenres")
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = False)
    
    book_genres = db.relationship("Book", back_populates="genre", foreign_keys="Book.genre_id")
    book_subgenres = db.relationship("Book", back_populates="subgenre", foreign_keys="Book.subgenre_id")
    # book_genres = db.relationship("Book", backref="genre", foreign_keys="Book.genre_id")
    # book_subgenres = db.relationship("Book", backref="subgenre", foreign_keys="Book.subgenre_id")
    
    def __init__(self, name):
        self.name = name