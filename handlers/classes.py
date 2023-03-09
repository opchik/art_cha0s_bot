from aiogram.fsm.state import State, StatesGroup

class Number(StatesGroup):
    text = State()
    number = State()

class Root(StatesGroup):
    catalog = State()
    profile = State()
    choose = State()

class Picture(StatesGroup):
    nickname = State()
    descript = State()
    pic_url = State()
    sub_tag = State()
    tag = State()
    yes_no = State()
    price = State()
    pic_name = State()

class Search(StatesGroup):
    filt = State()
    price = State()
    pic_name = State()
    sub_tag = State()
    tag = State()
    pic = State()
    sold = State()
    artist = State()