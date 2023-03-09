from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext 
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from db.db import CatalogBotDB
from aiogram.types.input_file import FSInputFile
from handlers.classes import Root, Search
from keyboard.keyboard import sub_tag, tag_classic, tag_modern, modern, classic, catalog, keyboard_start, pic_buttons, filter_but
from handlers.common import format_output_catalog
import os

router = Router()

@router.message(Root.catalog)
async def choose(message: Message, state: FSMContext) -> None:
	await state.update_data(sold=None, price=None, tag=None, pic_name=None, artist=None, pics_data=[], usr_id=None)
	reply_markup = ReplyKeyboardRemove()
	match message.text:
		case 'Просмотр':
			flag = await get_pic(message, state)
			if flag:
				await state.set_state(Search.pic)
			else:
				await state.set_state(Root.catalog)
				await message.answer(text="Упс... Ничего не найдено \nВыберите заново фильтр или смотрите все картины", reply_markup=catalog)

		case 'Фильтры':
			await state.set_state(Search.filt)
			await message.answer(text="Настройте фильтры и приступите у просмотру", reply_markup=filter_but)

		case "Выход":
			await state.set_state(Root.choose)
			await message.answer(text=f'Выберите действие', reply_markup=keyboard_start)

		case _:
			await state.set_state(Root.catalog)
			await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=catalog)


@router.message(Search.filt)
async def choose_filt(message: Message, state: FSMContext) -> None:
	match message.text:
		case "В наличии":
			await state.update_data(sold=False)
			await state.set_state(Search.filt)
			await message.answer(text="Выбраны только картины в наличии. \nВыберите дополнительный фильтр или приступите к просмотру", reply_markup=filter_but)

		case "Цена":
			await state.set_state(Search.price)
			await message.answer(text="Введите цену в формате \n(можно ввести только один предел):\n< мин. цена > : < макс. цена >", reply_markup=ReplyKeyboardRemove())

		case "Жанр":
			await state.set_state(Search.sub_tag)
			await message.answer(text=f"Выберите направление", reply_markup=sub_tag)


		case "Название":
			await state.set_state(Search.pic_name)
			await message.answer(text="Введите название картины. При вводе нескольких названий используйте пробел", reply_markup=ReplyKeyboardRemove())


		case "Автор":
			await state.set_state(Search.artist)
			await message.answer(text="Введите псевдоним или имя автора. При вводе нескольких авторов используйте пробел", reply_markup=ReplyKeyboardRemove())

		case "Просмотр":
			flag = await get_pic(message, state)
			if flag:
				await state.set_state(Search.pic)
			else:
				await state.set_state(Root.catalog)
				await message.answer(text="Упс... Ничего не найдено \nВыберите заново фильтр или смотрите все картины", reply_markup=catalog)

		case "Сбросить фильтры":
			await state.set_state(Root.catalog)
			await message.answer(text="Выберите фильтр или смотрите все картины", reply_markup=catalog)


		case _:
			await state.set_state(Search.filt)
			await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=filter_but)

			

 #------------------------------------------------------------------------------------------------------------------------------------
@router.message(Search.pic)
async def pic(message: Message, state: FSMContext) -> None:
	match message.text:
		case "Дальше":
			flag = await get_pic(message, state)
			if flag:
				await state.set_state(Search.pic)
			else:
				await state.set_state(Root.catalog)
				await message.answer(text="Упс... Ничего не найдено \nВыберите заново фильтр или смотрите все картины", reply_markup=catalog)

		case 'К работам автора':
			data = await state.get_data()
			await state.update_data(sold=None, price=None, tag=None, pic_name=None, artist=None, pics_data=[], usr_id=data['pics_data'][0][7])
			flag = await get_pic(message, state)
			if flag:
				await state.set_state(Search.pic)
			else:
				await state.set_state(Root.catalog)
				await message.answer(text="Упс... Ничего не найдено \nВыберите заново фильтр или смотрите все картины", reply_markup=catalog)

		case "Выход":
			await state.set_state(Root.catalog)
			await message.answer(text="Выберите фильтр или смотрите все картины", reply_markup=catalog)

		case _:
			await state.set_state(Search.pic)
			await message.answer(text='Выберите действие при помощи кнопки!', reply_markup=pic_buttons)


async def get_pic(message: Message, state: FSMContext) -> bool:
	data = await state.get_data()
	if len(data['pics_data']) > 1:
		del data['pics_data'][0]
		rows = data['pics_data'][0]
		await state.update_data(pics_data=data['pics_data'])
	else:
		pics = await CatalogBotDB.get_pic_fromDB(
			sold=data['sold'], 
			price=data['price'], 
			tag=data['tag'], 
			pic_name=data['pic_name'], 
			artist=data['artist'],
			usr_id=data['usr_id']
			)
		if not pics:
			return False
		await state.update_data(pics_data=pics)
		rows = pics[0]
	item = [rows[0], format_output_catalog(rows[1:])]
	try:
		await message.answer_photo(
			photo=FSInputFile(item[0]),
			caption=item[1],
			reply_markup=pic_buttons
			)
	except Exception:
		await message.answer(text="Картина была только что удалена, нажмите кнопку для продолжения просмотра", reply_markup=pic_buttons)
	return True

#-------------------------------------------------------------------------------------------------------------------------------------

@router.message(Search.sub_tag)
async def catalog_sub_tag(message: Message, state: FSMContext) -> None:
    if message.text and message.text in ("классика", "современное искусство", "Отмена"):
    	if message.text=="Отмена":
    		await state.set_state(Search.filt)
    		await message.answer(text="Выберите фильтр или приступите к просмотру", reply_markup=filter_but)
    	else:
            await state.set_state(Search.tag)
            if message.text == "современное искусство":
                await message.answer(text="Выберите жанр", reply_markup=tag_modern)
            elif message.text == "классика":
                await message.answer(text="Выберите жанр", reply_markup=tag_classic)

    else:
        await state.set_state(Search.sub_tag)
        await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=sub_tag)


@router.message(Search.tag)
async def catalog_tag(message: Message, state: FSMContext) -> None:
    if message.text and ((message.text in modern) or (message.text in classic)):
        await state.update_data(tag=message.text)
        await state.set_state(Search.filt)
        await message.answer(text="Жанр выбран. \nВыберите дополнительный фильтр или смотрите все картины", reply_markup=filter_but)
    else: 
        data = await state.get_data()
        await state.set_state(Search.tag)
        if data["sub_tag"] == "современное искусство":
            await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=tag_modern)
        elif data["sub_tag"] == "классика":
            await message.answer(text="Выберите действие при помощи кнопки!", reply_markup=tag_classic)


@router.message(Search.pic_name)
async def catalog_pic_name(message: Message, state: FSMContext) -> None:
	if message.text:
		arr = [i.lower()for i in message.text.split()]
		await state.update_data(pic_name=['%'+i+'%' for i in arr])
		await state.set_state(Search.filt)
		await message.answer(text="Названия добавлены. \nВыберите дополнительный фильтр или смотрите все картины", reply_markup=filter_but)

	else:
		await state.set_state(Search.pic_name)
		await message.answer(text="Введите название картины текстом!")



@router.message(Search.artist)
async def catalog_artist(message: Message, state: FSMContext) -> None:
	if message.text:
		await state.update_data(artist=[i.lower() for i in message.text.split()])
		await state.set_state(Search.filt)
		await message.answer(text="Имена добавлены. \nВыберите дополнительный фильтр или смотрите все картины", reply_markup=filter_but)

	else:
		await state.set_state(Search.artist)
		await message.answer(text="Введите творческие псевдонимы или имена авторов текстом")


def ok(s: str):
	if s:
		s = s.replace(' ', '')
		arr = s.split(":")
		if ":" in s and len(arr)==2:
			if (arr[0].isdigit() and arr[1].isdigit()) or (arr[0]=='' and arr[1].isdigit()) or (arr[1]=='' and arr[0].isdigit()):
				return arr
			else:
				return False
		else:
			return False
	else:
		return False


@router.message(Search.price)
async def catalog_artist(message: Message, state: FSMContext) -> None:
	price_from_message = ok(message.text)
	if price_from_message:
		if len(price_from_message[0]) <= 18 and len(price_from_message[1]) <= 18:
			await state.update_data(price=price_from_message)
			await state.set_state(Search.filt)
			await message.answer(text="Ценовой диапазон установлен. \nВыберите дополнительный фильтр или смотрите все картины", reply_markup=filter_but)
		else:
			await state.set_state(Search.price)
			await message.answer(text="Вы ввели слишком большую сумму, введите цену ещё раз")

	else:
		await state.set_state(Search.price)
		await message.answer(text="Неверный формат, введите цену ещё раз")