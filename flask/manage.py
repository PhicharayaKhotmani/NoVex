#Written by Kullatida Puranaphan
#650510655
from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.member import Member
from app.models.genre import Genre
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.favorite import Favorite
import datetime

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(Member(username = "phicharaya", email = "phicharaya@admin", password =generate_password_hash('1234',method='sha256'),
                                                    image_url='https://ui-avatars.com/api/?name=\สมชาย+ทรงแบด&background=83ee03&color=fff',
                                                    birthday = datetime.date(2003, 8, 1), is_writer=True, is_admin= True, deleted_at=None))
    db.session.add(Member(username = "AonAr21", email = "aonaon@hotmail.com", password =generate_password_hash('1234',method='sha256'),
                                                    image_url='https://ui-avatars.com/api/?name=\สมชาย+ทรงแบด&background=83ee03&color=fff',
                                                    birthday = datetime.date(2003, 7, 21), is_writer=True, is_admin= False, deleted_at=None))
    db.session.add(Genre(name="Fanfiction"))
    db.session.add(Genre(name="Original"))
    db.session.add(Genre(name="Translated"))
    db.session.add(Genre(name="Lovely"))
    db.session.add(Genre(name="Fantasy"))
    db.session.add(Genre(name="Boy Love"))
    db.session.add(Genre(name="Horror"))
    db.session.add(Book(member_id=2,name="ฆาตกรในวันสิ้นโลก", description = "ลึกแล้วๆในตัวทุกคนนั้นต่างมีความถูกต้องและความเชื่อเป็นของตัวเอง เขาไม่เคยเชื่อว่าเวรนั้นระงับด้วยการไม่จองเวร และนั่นคือสิ่งที่หยางเฟยหลิงเชื่อ",
                        image_url='https://i.pinimg.com/564x/16/e8/eb/16e8eb653a64c9ada23434ba1b435ea2.jpg',
                        genre_id = 1, subgenre_id =4, for_adult=True, deleted_at=None, deleted_by=None))
    db.session.add(Chapter(book_id=1, episode="0", titile="ประกาศ", content="นิยายเรื่องนี้ถูกสร้างมาจากจินตนาการนะคะ ไม่ได้มีความตั้งใจที่จะโจมตีใครหรือกลุ่มใด หากมีกาารกล่าวถึง ก็เป็นเพียงเพื่อให้ความสมจริงและมีมิติของเนื้อเรื่องเท่านั้น", deleted_at=None, deleted_by=None))
    db.session.commit()



if __name__ == "__main__":
    cli()
