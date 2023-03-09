from aiogram.filters.command import Command
from aiogram.filters.text import Text
from keyboard.keyboard import keyboard_start, profile, catalog
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
from handlers.classes import Root


router = Router()

@router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext) -> None:
    s = "Привет! Это art_cha0s бот.\n Здесь ты можешь публиковать, смотреть картины, находить контакты авторов и писать им лично, если тебя что-то заинтересовало. Что ж, давай начнем!"
    await state.set_state(Root.choose)
    await message.answer(text=s, reply_markup=keyboard_start)


@router.message(Root.choose)
async def choose_root(message: Message, state: FSMContext) -> None:
    match message.text:
        case "Портфолио":
            await state.set_state(Root.profile)
            await message.answer(text=f'Выберите действие', reply_markup=profile)

        case "Каталог":
            await state.set_state(Root.catalog)
            await message.answer(text="Выберите фильтр или приступите к просмотру", reply_markup=catalog)

        case _:
            await state.set_state(Root.choose)
            await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=keyboard_start)


# формат вывода --------------------------------------
def format_output_profile(rows):
    if rows[2] == "Пропустить описание":
        return f'Картина номер {rows[0]}\n\n{rows[3]}\n\nАвтор: {rows[4]}\nЦена: {rows[5]} ₽\n\n@art_cha0s | #{rows[1]}'
    else:
        return f'Картина номер {rows[0]}\n\n{rows[3]}\n\n{rows[2]}\n\nАвтор: {rows[4]}\nЦена: {rows[5]} ₽\n\n@art_cha0s | #{rows[1]}'     


def format_output_catalog(rows):
    if rows[1] == "Пропустить описание":
        return f'{rows[0]}\n\nАвтор: {rows[2]}\nЦена: {rows[3]} ₽\nДля связи: {rows[4]}\n\n@art_cha0s | #{rows[5]}'
    else:
        return f'{rows[0]}\n\n{rows[1]}\n\nАвтор: {rows[2]}\nЦена: {rows[3]} ₽\nДля связи: {rows[4]}\n\n@art_cha0s | #{rows[5]}'
        

def format_output_admin(rows):
    if rows[1] == "Пропустить описание":
        return f'{rows[2]}\n\nАвтор: {rows[5]}\nЦена: {rows[4]} ₽\n\n@art_cha0s | #{rows[0]}'
    else:
        return f'{rows[2]}\n\n{rows[1]}\n\nАвтор: {rows[5]}\nЦена: {rows[4]} ₽\n\n@art_cha0s | #{rows[0]}'