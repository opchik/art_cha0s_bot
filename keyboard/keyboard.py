from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

sub_genre = ("современное искусство", "классика")
modern = ("кубизм", "фавизм",  "футуризм", "поп-арт", "дадаизм", "сюрреализм", "экспрессионизм", "импрессионизм", "абстрактный_экспрессионизм") 
classic = ("портрет", "пейзаж", "марина", "анималистика", "бытовой", "натюрморт", "архитектура")

# кнопки для выбора действий: поиска или публикации-----------------------------------------------
buttons_start = [
        [
        KeyboardButton(text="Каталог"),
        KeyboardButton(text="Портфолио")
        ]
    ]
keyboard_start = ReplyKeyboardMarkup(
        keyboard=buttons_start,
        resize_keyboard=True
        )

# кнопки при входе в портфолио----------------------------------------------------------------------
button_profile = [
                [
                KeyboardButton(text='Опубликовать'),
                KeyboardButton(text='Мои картины')
                ],
                [
                KeyboardButton(text='Удалить'),
                KeyboardButton(text='Выход')
                ],
                [KeyboardButton(text='Отметить продажу'),]
        ]
profile = ReplyKeyboardMarkup(
        keyboard=button_profile,
        resize_keyboard=True 
        )

# кнопки каталога------------------------------------------------------------------------------------
button_catalog = [
                [
                KeyboardButton(text='Просмотр'),
                KeyboardButton(text='Фильтры'),
                KeyboardButton(text='Выход')
                ]        ]
catalog = ReplyKeyboardMarkup(
        keyboard=button_catalog,
        resize_keyboard=True 
        )

filt = [
        [
        KeyboardButton(text="В наличии"),
        KeyboardButton(text="Цена")
        ],
        [
        KeyboardButton(text="Жанр"),
        KeyboardButton(text="Название"),
        KeyboardButton(text="Автор")
        ],
        [
        KeyboardButton(text="Просмотр"),
        KeyboardButton(text="Сбросить фильтры"),
        ]
        ]
filter_but = ReplyKeyboardMarkup(
        keyboard=filt,
        resize_keyboard=True 
        )

# кнопки для возможных стилей живописи---------------------------------------------------------------
sub_tag_but = [[
                KeyboardButton(text=sub_genre[0]), 
                KeyboardButton(text=sub_genre[1])
                ],
                [KeyboardButton(text="Отмена")]
        ]
sub_tag = ReplyKeyboardMarkup(
        keyboard=sub_tag_but,
        resize_keyboard=True
        )

tag_but_classic = [
                [
                KeyboardButton(text=classic[0]),
                KeyboardButton(text=classic[1]), 
                KeyboardButton(text=classic[2]),
                ],
                [
                KeyboardButton(text=classic[3]),
                KeyboardButton(text=classic[4]),
                ],
                [
                KeyboardButton(text=classic[5]),
                KeyboardButton(text=classic[6])
                ]
        ]
tag_classic = ReplyKeyboardMarkup(
                keyboard=tag_but_classic,
                resize_keyboard=True
                )

tag_but_modern = [
                [
                KeyboardButton(text=modern[0]),
                KeyboardButton(text=modern[1]), 
                KeyboardButton(text=modern[2])
                ],
                [
                KeyboardButton(text=modern[3]),
                KeyboardButton(text=modern[4]),
                KeyboardButton(text=modern[5])
                ],
                [
                KeyboardButton(text=modern[6]),
                KeyboardButton(text=modern[7])
                ],
                [ KeyboardButton(text=modern[8]) ]
        ]
tag_modern = ReplyKeyboardMarkup(
                keyboard=tag_but_modern,
                resize_keyboard=True
                )
#-------------------------------------------------------------------------------------------------
# кнопка для пропуска описания картины-------------------------------------------------------
descript_but = ReplyKeyboardMarkup(
        keyboard = [[KeyboardButton(text="Пропустить описание")]],
        resize_keyboard=True
        )

# кнопки для отмены или принятия отправки данных о картине-------------------------------------------------
yes_no_but = [
        [
        KeyboardButton(text="Да, отправить")
        ],
        [
        KeyboardButton(text="Нет, отменить операцию")
        ]
    ]
yes_no = ReplyKeyboardMarkup(
        keyboard=yes_no_but,
        resize_keyboard=True
        )
#----------------------------------------------------------------------------------------------------

pic_buttons = ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text="Дальше")
                ],
                [
                KeyboardButton(text='К работам автора'),
                KeyboardButton(text="Выход")
                ]
                ],
        resize_keyboard=True
        )

# кнопки для проверки картин ---------------------------------------------------------------------------------

admin_but_yes_no = ReplyKeyboardMarkup(
        keyboard=[[ 
                KeyboardButton(text="Да"), 
                KeyboardButton(text="Нет")
                ],
                [KeyboardButton(text="Удалить данные пользователя")]],
        resize_keyboard=True
        )

admin_but_next = ReplyKeyboardMarkup(
        keyboard=[[ 
                KeyboardButton(text="Дальше")
                ]],
        resize_keyboard=True
        )

# отмена операции --------------------------------------------------------------------------------------------------

cancel_but = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True
        )

