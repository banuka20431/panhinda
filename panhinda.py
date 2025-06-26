from app import app, db
import sqlalchemy as sa
import sqlalchemy.orm as so

@app.shell_context_processor
def make_shell_context():
    from app.auth.models import User
    from app.articles.models import Article, Category, SubCategory

    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Article': Article, 'Category': Category, 'SubCategory': SubCategory}