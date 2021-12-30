import unittest
from app.models import Permission, User, AnonymousUser, Role

class UserModelTest(unittest.TestCase): 
    def test_password_setter(self): 
        u = User(email="a@example.com", password='cat')
        self.assertTrue(u.password_hash is not None)
    
    def test_no_password_getter(self): 
        u = User(email="b@example.com", password='cat')
        with self.assertRaises(AttributeError): 
            u.password
    
    def test_password_verification(self): 
        u = User(email="c@example.com", password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
    
    def test_password_salts_are_random(self): 
        u1 = User(email="d@example.com", password='cat')
        u2 = User(email="e@example.com", password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)
    
    def test_user_role(self): 
        u = User(email="f@example.com", password='cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.PURCHASE))
        self.assertFalse(u.can(Permission.SALE))
        self.assertFalse(u.can(Permission.MANAGE_GOODS))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_anonymous_user(self): 
        u = AnonymousUser() 
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.PURCHASE))
        self.assertFalse(u.can(Permission.SALE))
        self.assertFalse(u.can(Permission.MANAGE_GOODS))
        self.assertFalse(u.can(Permission.ADMIN))