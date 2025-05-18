from app.imports import *

class Party(StatesGroup):
    amount = State()
    
class RegisterAdmin(StatesGroup):
    password = State()
    
class BroadcastForm(StatesGroup):
    waiting_for_message = State()
    
class Investigate(StatesGroup):
    num = State()
    
class Logout(StatesGroup):
    captcha = State()
    
class Ban(StatesGroup):
    id = State()
    
class Registration(StatesGroup):
    name = State()
    country = State()