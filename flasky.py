import os
from app import create_app, db
from app.models import Address, Basket, Commodity, Commodity_category, Order, Payment, Store, User, Role
from flask_migrate import Migrate, upgrade

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context(): 
    return dict(db=db, User=User, Role=Role, Commodity_category=Commodity_category, Commodity=Commodity, Store=Store, Order=Order, Basket=Basket, Address=Address, Payment=Payment)

@app.cli.command()
def test(): 
    '''Run the unit tests'''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
def init(): 
    '''Insert roles in db.Role & Insert commodity_categories in db.Commodity_category & Insert payments in db.Payment'''
    Role.insert_roles()
    Commodity_category.insert_commodity_categories()
    Payment.insert_payments()