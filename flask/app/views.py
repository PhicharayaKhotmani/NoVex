import json
import secrets
import string
import datetime
import os
from flask import (jsonify, render_template,
                   request, url_for, flash, redirect)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse

from sqlalchemy.sql import text, desc
from flask_login import login_user, login_required, logout_user, current_user

from app import app
from app import db
from app import login_manager
from app import oauth

from app.models.member import Member
from app.models.genre import Genre
from app.models.book import Book
from app.models.favorite import Favorite
from app.models.chapter import Chapter

@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(int(user_id))


@app.route('/db')
def db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return '<h1>db works.</h1>'
    except Exception as e:
        return '<h1>db is broken.</h1>' + str(e)
    

@app.route('/crash')
def crash():
    return 1/0


def gen_avatar_url(email, name):
    bgcolor = generate_password_hash(email, method='sha256')[-6:]
    color = hex(int('0xffffff', 0) -
                int('0x'+bgcolor, 0)).replace('0x', '')
    lname = ''
    temp = name.split()
    fname = temp[0][0]
    if len(temp) > 1:
        lname = temp[1][0]


    avatar_url = "https://ui-avatars.com/api/?name=" + \
        fname + "+" + lname + "&background=" + \
        bgcolor + "&color=" + color
    return avatar_url




@app.route('/')
def home_page(): 
    testbook = Book.query.filter(Book.deleted_at == None).all()
    return render_template('homepage.html', books = testbook)


@app.route('/original')
def original_page():
    testbook = Book.query.filter(Book.deleted_at == None).all()
    return render_template('original_novel.html', books = testbook)

@app.route('/fanfic')
def fanfic_page():
    testbook = Book.query.filter(Book.deleted_at == None).all()
    return render_template('fanfic.html', books = testbook)

@app.route('/translated')
def translated_page():
    testbook = Book.query.filter(Book.deleted_at == None).all()
    return render_template('translated.html', books = testbook)


@app.route('/romantic_books')
def romantic_books():
    romantic_books = Book.query.filter_by(subgenre_id=4, deleted_at=None).all()
    return render_template('/subgenre/romantic.html', testbook=romantic_books)

@app.route('/fantasy_books')
def fantasy_books():
    fantasy_books = Book.query.filter_by(subgenre_id=5, deleted_at=None).all()
    return render_template('/subgenre/fantasy.html', testbook=fantasy_books)

@app.route('/ystation_books')
def ystation_books():
    ystation_books = Book.query.filter_by(subgenre_id=6, deleted_at=None).all()
    return render_template('/subgenre/y_station.html', testbook=ystation_books)

@app.route('/other_books')
def other_books():
    other_books = Book.query.filter_by(subgenre_id=7, deleted_at=None).all()
    return render_template('/subgenre/others.html', testbook=other_books)


@app.route('/books')
def books_homepage():

    def append_writer(books_):
        writer_name = books_.member.username #username of writer
        books_dict = books_.to_dict()
        books_dict["writer_name"] = writer_name #key value
        return books_dict
        
    books_ = Book.query.filter((Book.deleted_at == None)).order_by(Book.created_at).limit(6).all()
    books = list(map(append_writer, books_))
    # print(books_[0].member)
    app.logger.debug(f"DB Books: {books}")

    # db_books = Favorite.query.all()
    # print(list(map(lambda x: json.dumps(x), db_books)))
    # print(db_books[0].book_genres[0].to_dict())
    # books = list(map(lambda x: x.to_dict(), db_books))
    # app.logger.debug(f"DB My Favorite Books: {books}")

    return jsonify(books)


@app.route('/login', methods=('GET', 'POST'))
def login_page():

    if request.method == 'POST':
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')

        user = Member.query.filter_by(email=email).first()
 
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('login_page'))

        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home_page')
            return redirect(next_page)

    return render_template('login_page.html')


@app.route('/signup', methods=('GET', 'POST')) 
def signup_page():

    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
 
        validated = True
        validated_dict = {}
        valid_keys = ['username', 'email', 'password', 'birthday']


        # validate the input
        for key in result:
            app.logger.debug(str(key)+": " + str(result[key])) # { (username: test), ... }
            # screen of unrelated inputs
            if key not in valid_keys:
                continue


            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value
            # code to validate and add user to database goes here
        app.logger.debug("validation done")
        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            username = validated_dict['username']
            email = validated_dict['email']
            password = validated_dict['password']
            birthday = validated_dict['birthday']

            if (email != "admin@212" or email != "test@212"):
                is_admin = False


            is_writer = True
            # ถ้ามีเมลล์หรือชื่อ username อยู่แล้ว
            user = Member.query.filter_by(email=email).first() or Member.query.filter_by(username=username).first()
            if user:
                flash('Email address or username already exists')
                return redirect(url_for('login_page'))

            # create a new user with the form data. Hash the password so
            # the plaintext version isn't saved.
            app.logger.debug("preparing to add")
            avatar_url = gen_avatar_url(email, username)
            new_user = Member(email = email, username = username,
                                password = generate_password_hash(password, method='sha256'),
                                image_url = avatar_url, birthday = birthday, is_admin=is_admin, is_writer=is_writer)
            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('login_page'))
    return render_template('signup.html')


@app.route('/google/')
def google():

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

   # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    app.logger.debug(str(token))


    userinfo = token['userinfo']
    app.logger.debug(" Google User " + str(userinfo))
    email = userinfo['email']
    user = Member.query.filter_by(email=email).first()


    if not user:
        username = userinfo.get('given_name','') + " " + userinfo.get('family_name','')
        random_pass_len = 8
        password = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                          for i in range(random_pass_len))
        # picture = userinfo['picture']
        picture = gen_avatar_url(email, username)
        birthday = None
        if 'birthday' in userinfo:
            birthday = datetime.datetime.strptime(userinfo['birthday'], '%Y-%m-%d').date()

        if email != "admin@212":
            is_admin = False

        is_writer = True
        new_user = Member(email = email, username = username,
                                password = generate_password_hash(password, method='sha256'),
                                image_url = picture, birthday = birthday, is_admin=is_admin, is_writer=is_writer)
        db.session.add(new_user)
        db.session.commit()
        user = Member.query.filter_by(email=email).first()
    login_user(user)
    return redirect('/')


@app.route('/facebook/')
def facebook():
   
    oauth.register(
        name='facebook',
        client_id=app.config['FACEBOOK_CLIENT_ID'],
        client_secret=app.config['FACEBOOK_CLIENT_SECRET'],
        access_token_url='https://graph.facebook.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://www.facebook.com/dialog/oauth',
        authorize_params=None,
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'},
    )
    redirect_uri = url_for('facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@app.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    # app.logger.debug(str(token))

    resp = oauth.facebook.get(
        'https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    profile = resp.json()
    # print("Facebook User ", profile)

    userinfo = profile['name']
    app.logger.debug(" Facebook User " + str(userinfo))
    email = profile['email']
    user = Member.query.filter_by(email=email).first()

    if not user:
        random_pass_len = 8
        password = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                          for i in range(random_pass_len))
        picture = profile['picture']['data']['url']
        birthday = None

        if email != "admin@212":
            is_admin = False

        is_writer = True

        avatar_url = gen_avatar_url(email, userinfo)
        new_user = Member(email = email, username = userinfo,
                                password = generate_password_hash(password, method='sha256'),
                                image_url = avatar_url, birthday=birthday, is_admin=is_admin, is_writer=is_writer)
        db.session.add(new_user)
        db.session.commit()
        user = Member.query.filter_by(email=email).first()
    login_user(user)

    return redirect('/')


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('home_page'))

#Written by Kullatida Puranaphan 650510655
@app.route("/myFavorite/books")
@login_required
def myfav_db_books():
    
    def append_writer(favorite_book):
        writer_name = favorite_book.book.member.username #username
        favorite_book_dict = favorite_book.to_dict()
        favorite_book_dict["writer_name"] = writer_name #key value
        return favorite_book_dict
        
    myfav_db_books = Favorite.query.filter_by(member_id = current_user.id, deleted_at = None).order_by(desc(Favorite.updated_at))
    books = list(map(append_writer, myfav_db_books))
    # print(myfav_db_books)
    app.logger.debug(f"DB My Favorite Books: {books}")
    
    # books = []
    # db_books = Favorite.query.all()
    # print(list(map(lambda x: json.dumps(x), db_books)))
    # print(db_books[0].book_genres[0].to_dict())
    # books = list(map(lambda x: x.to_dict(), db_books))
    # app.logger.debug(f"DB My Favorite Books: {books}")
    # print(books)

    return jsonify(books)

@app.route('/myFavorite', methods=('GET', 'POST')) #Written by Kullatida Puranaphan 650510655
@login_required
def myFavorite():
    return render_template('myFavorite.html')

#Written by Kullatida Puranaphan 650510655
@app.route('/myFavorite/remove_fav_book', methods=('GET', 'POST'))
def remove_fav_book():
    app.logger.debug("MyFav - REMOVE")
    if request.method == 'POST':
        # result = request.form.to_dict()
        # id_ = result.get('id', '')
        # print(request.form)
        fav_id = request.form.get('id')
        # print(fav_id)
        # self = Favorite
        # print(type(id_))
        try:
            myfav_book = Favorite.query.get(fav_id)
            # print(myfav_book.member_id)
            if not myfav_book:
                return "No Book"
            if myfav_book.member_id == current_user.id:
                # db.session.delete(myfav_book)
                Favorite.soft_delete(myfav_book, myfav_book.member_id)
                db.session.commit()
        except Exception as ex:
           app.logger.error(f"Error removing favorite book with id {fav_id}: {ex}")
           raise
    return myfav_db_books()

@app.route("/respond", methods=('GET', 'POST'))
def respond():
    testbook = Book.query.filter(Book.deleted_at == None).all()
    return render_template('showbook.html', testbook=testbook)
def search_books(name):
    return Book.query.filter(
        Book.name.ilike(f"%{name}%"),Book.deleted_at == None).all()


@app.route('/search', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        search_type = request.form['search_type']
        search_term = request.form['search_term']
        
        if search_type == 'book_name':
            books = Book.query.filter(Book.name.ilike(f"%{search_term}%"), Book.deleted_at == None).all()
        elif search_type == 'genre':
            try:
                search_term_int = int(search_term)
                genre = Genre.query.filter(Genre.id == search_term_int).first()
            except ValueError:
                genre = Genre.query.filter(Genre.name.ilike(f"%{search_term}%")).first()
            if genre:
                books = genre.book_genres
            else:
                books = []
        elif search_type == 'member':
            if search_term:
                member = Member.query.filter(Member.username.ilike(f"%{search_term}%")).first()
                if member:
                    books = member.books
                else:
                    books = []
            else:

                books = Book.query.all()
        else:
            books = []
        return render_template('showbook.html', testbook=books)
    return render_template('search.html')

@app.route('/bookdesc/<int:book_id>')
@login_required
def book_description(book_id):
    if Book.for_adult:
        book = Book.query.get_or_404(book_id)
        chapters = Chapter.query.filter_by(book_id=book_id).all()
        #Written by Kullatida Puranaphan 650510655
        favorite = Favorite.query.filter_by(member_id=current_user.id, book_id=book_id, deleted_at = None).first()
        if favorite:
            return render_template('bookdesc.html', book=book, chapters=chapters, favorite=favorite)
        return render_template('bookdesc.html', book=book, chapters=chapters, favorite=favorite)
    else:
        flash('The book content is only for adults, please login.')
        return redirect(request.referrer or url_for('login_page'))
    
@app.route('/chapter/<int:chapter_id>')
def chapter_content(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('bookchapter.html', chapter=chapter)

# เพิ่มหนังสือ
@app.route('/addbook', methods=('GET','POST'))
@login_required
def addbook():
    if request.method == "POST":
        # data = request.form.to_dict()
        id = request.form['id']
        name = request.form['name']
        # genre = request.form['genre']
        genre = request.form.get('genre', None) 
        # subgenre = request.form['subgenre']
        subgenre = request.form.get('subgenre', None)
        description = request.form['description']
        image_url = request.form['imageUrl']  # รับ URL ของรูปภาพ


                    # สร้างและบันทึกข้อมูลในฐานข้อมูล
        new_book = Book(member_id=id, description=description,  
                        name=name, genre_id=genre, subgenre_id=subgenre,
                        image_url=image_url)

        db.session.add(new_book)

        db.session.commit()

    return redirect( url_for('writer_manage') )

# แก้ไขหนังสือ
@app.route('/edit/<int:book_id>', methods=['GET','POST'])
@login_required
def edit_book(book_id):
    data_book = Book.query.filter_by(id=book_id)
    # print('hello' , data_book)
    books = list(map(lambda x: x.to_dict(), data_book))
    return render_template('editbook.html', data_book=books, current_user=current_user)
    # if request.method == "POST":
    #     # data = request.form.to_dict()
    #     id = request.form['id']
    #     name = request.form['name']
    #     # genre = request.form['genre']
    #     genre = request.form.get('genre', None) 
    #     # subgenre = request.form['subgenre']
    #     subgenre = request.form.get('subgenre', None)
    #     description = request.form['description']
    #     image_url = request.form['imageUrl'] 

    # บันทึกการเปลี่ยนแปลงลงในฐานข้อมูล
        # db.session.commit()

    # return redirect(url_for('writer_manage'))

# หน้าจัดการหนังสือ
@app.route('/writermanage', methods=('GET','POST'))
@login_required
def writer_manage():
    # print('asdfghjkl;', dict(current_user))
    data_book = Book.query.filter_by(member_id=current_user.id, deleted_at=None)
    books = list(map(lambda x: x.to_dict(), data_book))
    return render_template('writer_manage.html', data=books)

# ดูว่ามีหนังสืออะไรบ้าง
@app.route('/writermanage/books')
@login_required
def writermanage_books_db():
    books = Book.query.filter_by(member_id=current_user.id)
    books_json = [book.to_dict() for book in books]
    return jsonify(books_json)

# ลบหนังสือออกจากระบบ
@app.route('/writermanage/remove_book/<int:book_id>', methods=('GET','POST'))
@login_required
def writermanage_remove_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book.member_id == current_user.id:
        Book.soft_delete(book, book.member_id)
        db.session.commit()

    return redirect( url_for('writer_manage') )

# หน้ารวมตอนในหนังสือ
@app.route('/bookpage/<int:book_id>', methods=('GET','POST'))
@login_required
def books_page(book_id):
    if request.method == 'POST':
        # Retrieve book_id from the form data
        chapter = request.form.get('id')
        #แสดงข้อมูลของหนังสือ
        # data_book = Book.query.filter_by(id=book_id)
        # data_chapter = Chapter.query.filter_by(id=chapter_id).all()
        # data_book = Book.query.filter_by(member_id=current_user.id, deleted_at=None)
    
    return render_template('book_page.html', data=chapter)

# ลบตอนออกจากระบบ
@app.route('/bookpage/remove_chapter/<int:chapter_id>')
@login_required
def bookpage_remove_chapter(chapter_id):
    # return render_template('write_page.html')
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    if chapter.member_id == current_user.id:
        chapter.soft_delete(current_user.id)
        db.session.commit()

    return redirect( url_for('books_page') )

@app.route('/addchapter/<int:chapter_id>')
def addchapter_write_page(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    if chapter.member_id == current_user.id:
        chapter.soft_delete(current_user.id)
        db.session.commit()

    return render_template('books_page.html')


@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/base')
def base_page():
    return render_template('base.html')

#Written by Kullatida Puranaphan 650510655
@app.route('/myFavorite/add_fav_book', methods=('GET','POST'))
def add_fav_book():
    if request.method == 'POST':
        # Retrieve book_id from the form data
        book_id = request.form.get('id')
        
        # Check if the book is already in favorites
        existing_favorite = Favorite.query.filter_by(member_id=current_user.id, book_id=book_id).first()
        if existing_favorite:
            if existing_favorite.deleted_at is not None:
                existing_favorite.deleted_at = None
                existing_favorite.deleted_by = None
                db.session.commit()
                return redirect(request.referrer)
            else:
                return redirect(request.referrer)
        
        # Create a new Favorite instance
        new_favorite = Favorite(member_id=current_user.id, book_id=book_id, deleted_at=None, deleted_by=None)
        # print(new_favorite)
        # Add the new favorite to the database
        db.session.add(new_favorite)
        db.session.commit()
        
        # return myfav_db_books()
        return redirect(request.referrer)
