from application import app
from support.models import db, Product
from werkzeug.security import generate_password_hash

def reset(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        test_product = Product(name="Snake Oil", price=9.99, stock=3)
        db.session.add(test_product)
        
        test_product2 = Product(name="Trump Steaks", price=999.99, stock=10)
        db.session.add(test_product2)
        db.session.commit()

if __name__ == "__main__":
    reset(app)
    print('Success. Database re-initialized.')
