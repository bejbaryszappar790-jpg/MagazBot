from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.enums import RegressButtonText


def reply_cancel_go_back_kb():

    keyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = RegressButtonText.GO_BACK), 
                                                KeyboardButton(text = RegressButtonText.CANCEL)] 
                                                ],
                                                resize_keyboard = True
                                                )

    return keyboard