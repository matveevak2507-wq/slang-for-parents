from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), unique=True, nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    origin = db.Column(db.Text)
    image_name = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id', ondelete='SET NULL'))
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255))
    correct_options = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class FillBlankTask(db.Model):
    __tablename__ = 'fill_blank_tasks'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id', ondelete='SET NULL'))
    sentence = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    origin = db.Column(db.Text)
    image_name = db.Column(db.String(255))
    user_contact = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending', nullable=False)
    admin_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())