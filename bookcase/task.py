from datetime import datetime

from flask_apscheduler.scheduler import APScheduler

from . import db
from bookcase.models import Book

scheduler = APScheduler()

def overdue_check():
    print("Performing check")
    app = scheduler.app
    with app.app_context():
        book = Book.query.all()
        for data in book:
            try:
                if data.due_date < datetime.now().date():
                    data.overdue = True
            except Exception as e:
                print(str(e))
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        db.session.close()
    return str('ok')
                    