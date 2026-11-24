import os
import uuid
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, send_from_directory)

from config import Config
from models import db, Word, QuizQuestion, FillBlankTask, Suggestion


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    return app


app = create_app()


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


def _save_image(file_storage, prefix):
    if not file_storage or not file_storage.filename:
        return None
    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        return None
    name = f"{prefix}_{uuid.uuid4().hex}{ext}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], name))
    return name


def _option_text(q, letter):
    letter = (letter or "").lower().strip()
    return {"a": q.option_a, "b": q.option_b, "c": q.option_c,
            "d": q.option_d or ""}.get(letter, "—")


def _score_color(score, total):
    if total == 0:
        return "#c62828", "Нет данных."
    pct = score / total * 100
    if pct < 25:
        return "#c62828", "Не расстраивайтесь — попробуйте ещё раз!"
    if pct < 50:
        return "#f57c00", "Неплохо! Продолжайте тренироваться."
    if pct < 75:
        return "#fbc02d", "Хороший результат! Вы на верном пути."
    return "#2e7d32", "Так держать, Вы молодцы!"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dictionary")
def dictionary():
    words = Word.query.filter_by(status="approved").order_by(Word.word).all()
    grouped = {}
    for w in words:
        grouped.setdefault(w.word[0].upper(), []).append(w)
    return render_template("dictionary.html", grouped=sorted(grouped.items()))


@app.route("/word/<int:word_id>")
def word_page(word_id):
    word = Word.query.get_or_404(word_id)
    return render_template("word.html", word=word)


# ---------- Викторина ----------

def _build_quiz(limit=20):
    return QuizQuestion.query.order_by(db.func.rand()).limit(limit).all()


@app.route("/quiz")
def quiz_start():
    session.pop("quiz_items", None)
    session.pop("quiz_answers", None)
    qs = _build_quiz()
    if not qs:
        flash("Вопросы пока не добавлены.", "error")
        return redirect(url_for("index"))
    session["quiz_items"] = [q.id for q in qs]
    session["quiz_answers"] = {}
    return redirect(url_for("quiz_item", num=1))


@app.route("/quiz/<int:num>", methods=["GET", "POST"])
def quiz_item(num):
    item_ids = session.get("quiz_items")
    if not item_ids:
        return redirect(url_for("quiz_start"))
    total = len(item_ids)
    if num < 1 or num > total:
        return redirect(url_for("quiz_item", num=1))

    answers = session.get("quiz_answers", {})

    if request.method == "POST":
        action = request.form.get("action")
        answers[str(num)] = request.form.get("answer", "")
        session["quiz_answers"] = answers
        session.modified = True

        if action == "back" and num > 1:
            return redirect(url_for("quiz_item", num=num - 1))
        if action == "next" and num < total:
            return redirect(url_for("quiz_item", num=num + 1))
        if action == "finish":
            return redirect(url_for("quiz_results"))
        return redirect(url_for("quiz_item", num=num))

    q = QuizQuestion.query.get(item_ids[num - 1])
    if not q:
        return redirect(url_for("quiz_item", num=min(num + 1, total)))

    current = answers.get(str(num), "")

    options = [("a", q.option_a), ("b", q.option_b), ("c", q.option_c)]
    if q.option_d:
        options.append(("d", q.option_d))

    return render_template(
        "quiz.html", q=q, num=num, total=total, options=options,
        current_answer=current,
    )


@app.route("/quiz/results")
def quiz_results():
    item_ids = session.pop("quiz_items", None)
    answers = session.pop("quiz_answers", {}) or {}
    if not item_ids:
        flash("Результат уже был показан. Пройдите тест заново.", "info")
        return redirect(url_for("quiz_start"))

    details = []
    score = 0
    for i, qid in enumerate(item_ids, start=1):
        q = QuizQuestion.query.get(qid)
        if not q:
            continue
        user_ans = answers.get(str(i), "")
        correct_set = [x.strip() for x in q.correct_options.split(",") if x.strip()]
        ok = user_ans.lower() in correct_set
        if ok:
            score += 1
        details.append({
            "question": q.question,
            "user_answer": _option_text(q, user_ans) if user_ans else "—",
            "correct_answer": ", ".join(_option_text(q, c) for c in correct_set),
            "is_correct": ok,
        })

    total = len(details)
    color, message = _score_color(score, total)
    return render_template(
        "results.html", details=details, score=score, total=total,
        color=color, message=message,
        retry_url=url_for("quiz_start"), title="Викторина",
    )


# ---------- Пропуски ----------

def _build_fills(limit=20):
    return FillBlankTask.query.order_by(db.func.rand()).limit(limit).all()


@app.route("/fill-blank")
def fill_start():
    session.pop("fill_items", None)
    session.pop("fill_answers", None)
    fs = _build_fills()
    if not fs:
        flash("Задания пока не добавлены.", "error")
        return redirect(url_for("index"))
    session["fill_items"] = [f.id for f in fs]
    session["fill_answers"] = {}
    return redirect(url_for("fill_item", num=1))


@app.route("/fill-blank/<int:num>", methods=["GET", "POST"])
def fill_item(num):
    item_ids = session.get("fill_items")
    if not item_ids:
        return redirect(url_for("fill_start"))
    total = len(item_ids)
    if num < 1 or num > total:
        return redirect(url_for("fill_item", num=1))

    answers = session.get("fill_answers", {})

    if request.method == "POST":
        action = request.form.get("action")
        answers[str(num)] = request.form.get("answer", "").strip()
        session["fill_answers"] = answers
        session.modified = True

        if action == "back" and num > 1:
            return redirect(url_for("fill_item", num=num - 1))
        if action == "next" and num < total:
            return redirect(url_for("fill_item", num=num + 1))
        if action == "finish":
            return redirect(url_for("fill_results"))
        return redirect(url_for("fill_item", num=num))

    f = FillBlankTask.query.get(item_ids[num - 1])
    if not f:
        return redirect(url_for("fill_item", num=min(num + 1, total)))

    current = answers.get(str(num), "")

    return render_template(
        "fill_blank.html", f=f, num=num, total=total,
        current_answer=current,
    )


@app.route("/fill-blank/results")
def fill_results():
    item_ids = session.pop("fill_items", None)
    answers = session.pop("fill_answers", {}) or {}
    if not item_ids:
        flash("Результат уже был показан. Пройдите тест заново.", "info")
        return redirect(url_for("fill_start"))

    details = []
    score = 0
    for i, fid in enumerate(item_ids, start=1):
        f = FillBlankTask.query.get(fid)
        if not f:
            continue
        user_ans = answers.get(str(i), "")
        ok = user_ans.strip().lower() == f.correct_answer.strip().lower()
        if ok:
            score += 1
        details.append({
            "question": f.sentence,
            "user_answer": user_ans or "—",
            "correct_answer": f.correct_answer,
            "is_correct": ok,
        })

    total = len(details)
    color, message = _score_color(score, total)
    return render_template(
        "results.html", details=details, score=score, total=total,
        color=color, message=message,
        retry_url=url_for("fill_start"), title="Вставьте пропуски",
    )


# ---------- Форма предложки ----------

@app.route("/suggest", methods=["GET", "POST"])
def suggest():
    if request.method == "POST":
        word_text = request.form.get("word", "").strip()
        meaning = request.form.get("meaning", "").strip()

        if not word_text:
            flash("Слово обязательно.", "error")
            return redirect(url_for("suggest"))

        image_name = _save_image(request.files.get("image"), "sugg")

        db.session.add(Suggestion(
            word=word_text, meaning=meaning or "—",
            image_name=image_name, status="pending",
        ))
        db.session.commit()
        flash("Ваше слово отправлено на рассмотрение!", "success")
        return redirect(url_for("suggest"))

    return render_template("suggest.html")


# ---------- Админ ----------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == app.config["ADMIN_USERNAME"] and p == app.config["ADMIN_PASSWORD"]:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        flash("Неверный логин или пароль", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_panel():
    suggestions = Suggestion.query.filter_by(status="pending") \
        .order_by(Suggestion.created_at.desc()).all()
    words = Word.query.order_by(Word.word).all()
    return render_template("admin_panel.html", suggestions=suggestions, words=words)


@app.route("/admin/suggestion/<int:sid>/approve", methods=["POST"])
@admin_required
def admin_approve(sid):
    s = Suggestion.query.get_or_404(sid)
    existing = Word.query.filter_by(word=s.word).first()
    if existing:
        existing.meaning = s.meaning
        if s.image_name:
            existing.image_name = s.image_name
    else:
        db.session.add(Word(
            word=s.word, meaning=s.meaning,
            image_name=s.image_name, status="approved",
        ))
    s.status = "approved"
    db.session.commit()
    flash("Слово добавлено в словарь.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/suggestion/<int:sid>/reject", methods=["POST"])
@admin_required
def admin_reject(sid):
    s = Suggestion.query.get_or_404(sid)
    s.status = "rejected"
    db.session.commit()
    flash("Слово отклонено.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/suggestion/<int:sid>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_suggestion(sid):
    s = Suggestion.query.get_or_404(sid)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "reject":
            s.status = "rejected"
            db.session.commit()
            flash("Предложение отклонено.", "success")
            return redirect(url_for("admin_panel"))

        s.word = request.form.get("word", s.word).strip()
        s.meaning = request.form.get("meaning", s.meaning).strip()
        new_img = _save_image(request.files.get("image"), "sugg")
        if new_img:
            s.image_name = new_img

        if action == "approve":
            existing = Word.query.filter_by(word=s.word).first()
            if existing:
                existing.meaning = s.meaning
                if s.image_name:
                    existing.image_name = s.image_name
            else:
                db.session.add(Word(
                    word=s.word, meaning=s.meaning,
                    image_name=s.image_name, status="approved",
                ))
            s.status = "approved"
            db.session.commit()
            flash("Слово одобрено и добавлено в словарь.", "success")
            return redirect(url_for("admin_panel"))

        db.session.commit()
        flash("Изменения сохранены.", "success")
        return redirect(url_for("admin_panel"))

    return render_template("admin_edit_suggestion.html", s=s)


@app.route("/admin/word/<int:wid>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_word(wid):
    w = Word.query.get_or_404(wid)
    if request.method == "POST":
        w.word = request.form.get("word", w.word).strip()
        w.meaning = request.form.get("meaning", w.meaning).strip()
        new_img = _save_image(request.files.get("image"), f"word{wid}")
        if new_img:
            w.image_name = new_img
        db.session.commit()
        flash("Слово обновлено.", "success")
        return redirect(url_for("admin_panel"))
    return render_template("admin_edit_word.html", word=w)


@app.route("/admin/question/new", methods=["GET", "POST"])
@admin_required
def admin_new_question():
    if request.method == "POST":
        correct = request.form.getlist("correct")
        if not correct:
            flash("Выберите хотя бы один правильный вариант.", "error")
            return redirect(url_for("admin_new_question"))
        db.session.add(QuizQuestion(
            question=request.form["question"].strip(),
            option_a=request.form["option_a"].strip(),
            option_b=request.form["option_b"].strip(),
            option_c=request.form["option_c"].strip(),
            option_d=(request.form.get("option_d") or "").strip() or None,
            correct_options=",".join(sorted(correct)),
        ))
        db.session.commit()
        flash("Вопрос добавлен.", "success")
        return redirect(url_for("admin_panel"))
    return render_template("admin_new_question.html")


@app.route("/admin/fill/new", methods=["GET", "POST"])
@admin_required
def admin_new_fill():
    if request.method == "POST":
        db.session.add(FillBlankTask(
            sentence=request.form["sentence"].strip(),
            correct_answer=request.form["correct_answer"].strip(),
        ))
        db.session.commit()
        flash("Задание добавлено.", "success")
        return redirect(url_for("admin_panel"))
    return render_template("admin_new_fill.html")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)