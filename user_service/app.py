from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import re
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)

engine = create_engine('sqlite:///users.db')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

Base.metadata.create_all(engine)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    username = data.get('username')
    email = data.get('email')
    password1 = data.get('password1')
    password2 = data.get('password2')

    if not username or not email or not password1 or not password2:
        return jsonify({'error': 'Все поля обязательны'}), 400
    if password1 != password2:
        return jsonify({'error': 'Пароли не совпадают'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Некорректный email'}), 400
    if len(password1) < 8:
        return jsonify({'error': 'Пароль слишком короткий (мин. 8 символов)'}), 400

    db = SessionLocal()
    if db.query(User).filter_by(username=username).first():
        db.close()
        return jsonify({'error': 'Пользователь уже существует'}), 400
    if db.query(User).filter_by(email=email).first():
        db.close()
        return jsonify({'error': 'Email уже используется'}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password1)
    )
    db.add(user)
    db.commit()
    db.close()
    return jsonify({'status': 'registered'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    db.close()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Неверные учетные данные'}), 401
    return jsonify({'status': 'logged_in', 'username': username}), 200

@app.route('/profile/<username>', methods=['GET'])
def profile(username):
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    db.close()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'username': user.username, 'email': user.email}), 200

admin = Admin(app, name='User Admin', template_mode='bootstrap3')
admin.add_view(ModelView(User, SessionLocal()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
