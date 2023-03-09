from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram import Router
from db.db import ClientBotDB
from keyboard.keyboard import keyboard_start, profile, sub_tag, cancel_but
from aiogram.types.input_file import FSInputFile
from handlers.common import format_output_profile
from handlers.classes import Picture, Root, Number
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup


router = Router()
	

@router.message(Root.profile)
async def choose(message: Message, state: FSMContext) -> None:
	match message.text:
		case "Мои картины":
			await process_nickname(message)
			await state.set_state(Root.profile)
			await message.answer(text=f'Выберите действие', reply_markup=profile)


		case "Отметить продажу":
			await state.update_data(text=message.text)
			await state.set_state(Number.number)
			await message.answer(text="Введите номер картины", reply_markup=cancel_but)

		case "Удалить":
			await state.update_data(text=message.text)
			await state.set_state(Number.number)
			await message.answer(text="Введите номер картины", reply_markup=cancel_but)

		case "Опубликовать":
			reply_markup=ReplyKeyboardRemove()
			res = await ClientBotDB.nickname_exist(message.from_user.id)
			if len(res) != 0:
				await state.set_state(Picture.sub_tag)
				await message.answer(
					text=f"Привет, {res[0][0]}!\nВыберите направление.",
					reply_markup=sub_tag
					)
			else:
				await state.set_state(Picture.nickname)
				await message.answer(text="Введите своё имя или творческий псевдоним. Обдумайте все прежде чем сделать выбор, сменить его не получится", reply_markup=cancel_but)

		case "Выход":
			await state.set_state(Root.choose)
			await message.answer(text=f'Выберите действие', reply_markup=keyboard_start)

		case _:
			await state.set_state(Root.profile)
			await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=profile)


# просмотр всех картин
async def process_nickname(message: Message) -> None:
	pics = await ClientBotDB.get_profile(message.from_user.id)
	for rows in pics:
		item = [rows[0], format_output_profile(rows[1:])]
		await message.answer_photo(
			photo=FSInputFile(item[0]),
			caption=item[1],
			reply_markup=ReplyKeyboardRemove()
			)


@router.message(Number.number)
async def process_description(message: Message, state: FSMContext) -> None:
	await state.update_data(number=message.text)
	data = await state.get_data()
	if message.text and (message.text.isdigit() or message.text=="Отмена"):
		if message.text=="Отмена":
			await state.set_state(Root.profile)
			await message.answer(text=f'Выход выполнен.\nВыберите действие', reply_markup=profile)

		elif data['text'] == "Отметить продажу":
			flag = await ClientBotDB.sale(message.from_user.id, int(data['number']))
			if flag:
				await state.set_state(Root.profile)
				await message.answer(text=f'Продажа отмечена.\nВыберите действие', reply_markup=profile)
			else:
				await state.set_state(Number.number)
				await message.answer(text="Картины с таким номером нет. Введите существующий номер картины", reply_markup=cancel_but)

		elif data['text'] == "Удалить":
			flag = await ClientBotDB.del_pic(message.from_user.id, int(data['number']))
			if flag:
				await state.set_state(Root.profile)
				await message.answer(text=f'Картина удалена.\nВыберите действие', reply_markup=profile)
			else:
				await state.set_state(Number.number)
				await message.answer(text="Картины с таким номером нет. Введите существующий номер картины", reply_markup=cancel_but)

	else:
		await state.set_state(Number.number)
		await message.answer(text="Неверный формат. \nВведите номер картины или нажмите кнопку", reply_markup=cancel_but)