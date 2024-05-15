from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Weather"),
                                      KeyboardButton(text="Calculator"),
                                      KeyboardButton(text="Searcher"),
                                      KeyboardButton(text="Convertor"),
                                      ]], resize_keyboard=True)
