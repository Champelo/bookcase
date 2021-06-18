# from bookcase import db, models
# from datetime import datetime

# def check_overdue():
#     books = db.session.query(models.Book).filter_by(status=False)
#     for book in books:
#         if book.due_date < datetime.now():
#             book.overdue = True
#             borrower = db.session.query(models.Borrower).filter_by(book.borrower_id).first()
#             borrower.rating -= 1
            