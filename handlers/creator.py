from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from keyboard.keyboard import yes_no, sub_tag, tag_classic, tag_modern, profile, descript_but
from keyboard.keyboard import modern, classic, cancel_but
from db.db import ClientBotDB
from bot import bot
from handlers.classes import Root, Picture
import os

router = Router()
    
# начало блока публикации

@router.message(Picture.nickname)
async def process_nickname(message: Message, state: FSMContext) -> None:
    if message.text:
        if message.text=="Отмена":
            await state.clear()
            await state.set_state(Root.profile)
            await message.answer(text="Выберите действие", reply_markup=profile)
        else:
            await state.update_data(nickname=message.text)
            await ClientBotDB.add_nickname(message.from_user.id, message.text, message.from_user.username)
            await state.set_state(Picture.sub_tag)
            await message.answer(text=f"Привет, {message.text}!\nВыберите направление", reply_markup=sub_tag)

    else:
        await state.set_state(Picture.nickname)
        await message.answer(text="Неверный формат. Введите свой творческий псевдоним ещё раз", reply_markup=cancel_but)



@router.message(Picture.sub_tag)
async def process_sub_tag(message: Message, state: FSMContext) -> None:
    if message.text and message.text in ("классика", "современное искусство", "Отмена"):
        if message.text=="Отмена":
            await state.clear()
            await state.set_state(Root.profile)
            await message.answer(text="Выберите действие", reply_markup=profile)
        else:
            await state.update_data(sub_tag=message.text)
            await state.set_state(Picture.tag)
            if message.text == "современное искусство":
                await message.answer(text="Выберите направление", reply_markup=tag_modern)
            elif message.text == "классика":
                await message.answer(text="Выберите направление", reply_markup=tag_classic)

    else:
        await state.set_state(Picture.sub_tag)
        await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=sub_tag)


@router.message(Picture.tag)
async def process_tag(message: Message, state: FSMContext) -> None:
    if message.text and ((message.text in modern) or (message.text in classic)):
        await state.update_data(tag=message.text)
        await state.set_state(Picture.pic_name)
        await message.answer(text="Введите название картины", reply_markup=ReplyKeyboardRemove())

    else:
        data = await state.get_data()
        await state.set_state(Picture.tag)
        if data["sub_tag"] == "современное искусство":
            await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=tag_modern)
        elif data["sub_tag"] == "классика":
            await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=tag_classic)


@router.message(Picture.pic_name)
async def process_pic_name(message: Message, state: FSMContext) -> None:
    if message.text:
        await state.update_data(pic_name=message.text)
        await state.set_state(Picture.descript)
        await message.answer(text="Введите описание", reply_markup=descript_but)

    else:
        await state.set_state(Picture.pic_name)
        await message.answer(text="Введите название картины текстом", reply_markup=ReplyKeyboardRemove())


@router.message(Picture.descript)
async def process_descript(message: Message, state: FSMContext) -> None:
    if message.text:
        await state.update_data(descript=message.text)
        await state.set_state(Picture.price)
        await message.answer(text="Введите цену (руб.)", reply_markup=ReplyKeyboardRemove())

    else:
        await state.set_state(Picture.descript)
        await message.answer(text="Введите описание", reply_markup=descript_but)


@router.message(Picture.price)
async def process_price(message: Message, state: FSMContext) -> None:
    if message.text and message.text.isdigit():
        if len(message.text) <= 18:
            await state.update_data(price=message.text)
            await state.set_state(Picture.pic_url)
            await message.answer(text="Загрузите фото картины")
        else:
            await state.set_state(Picture.price)
            await message.answer(text="Вы ввели слишком большую сумму.\nВведите цену ещё раз (руб.)")

    else:
        await state.set_state(Picture.price)
        await message.answer(text="Введите цену числом (руб.)")


@router.message(Picture.pic_url)
async def process_pic_url(message: Message, state: FSMContext) -> None:
    if message and message.photo:
        path = await post_del_pics(message, post=True)
        await state.update_data(pic_url=path)
        await message.answer(text=f"Опубликовать картину?", reply_markup=yes_no)
        await state.set_state(Picture.yes_no)
    else:
        await state.set_state(Picture.pic_url)
        await message.answer(text="Неверный формат!\nЗагрузите фото картины")



@router.message(Picture.yes_no)
async def post_or_not(message: Message, state: FSMContext) -> None:
    stoka = ("Нет, отменить операцию","Да, отправить")
    if message.text and message.text in stoka:
        await state.update_data(yes_no=message.text)
        user_data = await state.get_data()
        if message.text==stoka[0]:
            await post_del_pics(message, del_pic=user_data['pic_url'])
            await message.answer(
                text="Действие отменено. \nВыберите действие",
                reply_markup=profile
                )
        else:
            await ClientBotDB.add_to_db(user_data['pic_url'], user_data['tag'], user_data['descript'], message.from_user.id, user_data['price'], user_data['pic_name'])
            await message.answer(
                text="Картина отправлена на модерацию. \nВыберите действие",
                reply_markup=profile
                )
        await state.clear()
        await state.set_state(Root.profile)

    else:
        await message.answer(text=f"Выберите действие при помощи кнопки!\nОпубликовать картину?", reply_markup=yes_no)
        await state.set_state(Picture.yes_no)

# конец блока публикации-----------------------------------------------------------------------------------------------------------

# сохранение и удаление картины после публикации
async def post_del_pics(message: Message, post=None, del_pic=None):
    if post is not None:
        destination = f"/root/photos/{message.from_user.id}"
        if not os.path.exists(destination):
            os.mkdir(destination)
        name = f"{message.photo[-1].file_id}.png"
        path = os.path.join(destination, name)
        await bot.download(
                message.photo[-1],
                destination=path
                )
        return path

    elif del_pic is not None:
        os.remove(del_pic)


