from keyboard.keyboard import admin_but_yes_no, admin_but_next, cancel_but
from aiogram.filters.text import Text
from aiogram.filters.command import Command
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from db.db import AdminBotDB
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
from aiogram.types.input_file import FSInputFile
from bot import bot
from handlers.common import format_output_admin

class Choose(StatesGroup):
    yes_no = State()
    next_pic = State()
    no = State()
    sure = State()

router = Router()


@router.message(Command(commands=["begin"]))
async def chat_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Choose.next_pic)
    await message.answer(
        text="Начните проверку картин", 
        reply_markup=admin_but_next
        )


@router.message(Choose.next_pic)
async def check_pics(message: Message, state: FSMContext) -> None:
    match message.text:
        case "Дальше":
            pic = await AdminBotDB.get_pic()
            if pic:
                await state.update_data(pic_url=pic[0][0], name=pic[0][3], usr_id=pic[0][4])
                item = [pic[0][0], format_output_admin(pic[0][1:])]
                await message.answer_photo(
                    photo=FSInputFile(item[0]),
                    caption=item[1],
                    reply_markup=admin_but_yes_no
                )
                await state.set_state(Choose.yes_no)

            else: 
                await state.set_state(Choose.next_pic)
                await message.answer(
                    text="Пока никто ничего не добавил", 
                    reply_markup=admin_but_next
                    )

        case _:
            await state.set_state(Choose.next_pic)
            await message.answer(
                text="Выберите действие при помощи кнопки!", 
                reply_markup=admin_but_next
                )


@router.message(Choose.yes_no)
async def check_pics(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    match message.text:
        case "Да":
            await AdminBotDB.add_pic(data['pic_url'], data['usr_id'])
            await state.clear()
            await state.set_state(Choose.next_pic)
            await message.answer(
                text='Картина добавлена в основную галерею', 
                reply_markup=admin_but_next
                )
            await bot.send_message(
                text=f'📝 Картина "{data["name"]}" добавлена в основную галерею 📝', 
                chat_id=data['usr_id']
                )

        case "Нет":
            await AdminBotDB.del_pic(data['pic_url'])
            await state.set_state(Choose.no)
            await message.answer(
                text="Введите причину отказа или предупреждение", 
                reply_markup=ReplyKeyboardRemove()
                )

        case "Удалить данные пользователя":
            await state.set_state(Choose.sure)
            await message.answer("Вы уверены, что хотите удалить данные?\nЕсли да - введите причину", reply_markup=cancel_but)

        case _:
            await state.set_state(Choose.yes_no)
            await message.answer(
                text="Выберите действие при помощи кнопки!", 
                reply_markup=admin_but_yes_no
                )

@router.message(Choose.no)
async def del_pics(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await state.set_state(Choose.next_pic)
    await message.answer(
        text="Причина отправлена пользователю", 
        reply_markup=admin_but_next
        )
    await bot.send_message(
        text=f'📝 Картина "{data["name"]}" не прошла проверку.\n{message.text} 📝',
        chat_id=data['usr_id']
        )

@router.message(Choose.sure)
async def del_profile(message: Message, state: FSMContext) -> None:
    if message.text:
        if message.text=="Отмена":
            await state.clear()
            await state.set_state(Choose.next_pic)
            await message.answer(text="Действие отменено", reply_markup=admin_but_next)
        else:
            data = await state.get_data()
            await AdminBotDB.delete_profile(data['usr_id'])
            await state.clear()
            await state.set_state(Choose.next_pic)
            await message.answer(
                text="Профиль удален.\nПричина отправлена пользователю", 
                reply_markup=admin_but_next
                )
            await bot.send_message(
                text=f'📝 Ваш профиль удален.\n{message.text} 📝',
                chat_id=data['usr_id']
                )
    else:
        await state.set_state(Choose.sure)
        await message.answer("Неверный формат, введите текст.\nВы уверены, что хотите удалить данные?\nЕсли да - введите причину", reply_markup=cancel_but)


