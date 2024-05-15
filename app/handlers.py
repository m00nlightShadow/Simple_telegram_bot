from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import requests
import numexpr as ne

import app.keyboards as kb
from app.utils import get_location_name

from config import WEATHER_API, SEARCHER_API, SEARCH_ENGINE_ID, CONVERTOR_API


router = Router()


class Reg(StatesGroup):
    city = State()
    calculator = State()
    searcher = State()
    base_curr = State()
    target_curr = State()
    curr_amount = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    print('Start')
    await message.reply("Hello friend. What can I do for you? Make a choice in menu below.", reply_markup=kb.main)


@router.message(F.text == 'Weather')
async def weather(message: Message, state: FSMContext):
    await state.set_state(Reg.city)
    await message.answer('Enter your town, please')


@router.message(Reg.city)
async def get_weather(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    city_data = await state.get_data()
    city = get_location_name(city_data['city'].lower().strip())
    res = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric')
    if res.status_code == 200 and city:
        data = res.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        feels_like_temp = data['main']['feels_like']
        wind = data['wind']['speed']
        await message.answer(f"{city}, {weather_description}. "
                             f"Temperature: {temperature}°C, "
                             f"feels like {feels_like_temp}°C. "
                             f"Wind {wind} m/s", reply_markup=kb.main)
        await state.clear()
    else:
        await message.reply("Error fetching weather data", reply_markup=kb.main)
        await state.clear()


@router.message(F.text == 'Calculator')
async def calculator(message: Message, state: FSMContext):
    await state.set_state(Reg.calculator)
    await message.answer('What would you like to calculate?\n'
                         '(Please use * instead x to multiply)')


@router.message(Reg.calculator)
async def calculate(message: Message, state: FSMContext):
    await state.update_data(calculator=message.text)
    data = await state.get_data()
    try:
        result = ne.evaluate(data['calculator'])
        print(data['calculator'])
        await message.reply(f'{result}', reply_markup=kb.main)
    except Exception as e:
        await message.reply(f"Can't calculate {data['calculator']}. Please try again", reply_markup=kb.main)
    finally:
        await state.clear()


@router.message(F.text == 'Searcher')
async def searcher(message: Message, state: FSMContext):
    await state.set_state(Reg.searcher)
    await message.answer('Enter your request please')


@router.message(Reg.searcher)
async def search(message: Message, state: FSMContext):
    await state.update_data(searcher=message.text)
    state_data = await state.get_data()
    search_data = state_data['searcher']
    url = f"https://www.googleapis.com/customsearch/v1?key={SEARCHER_API}&cx={SEARCH_ENGINE_ID}&q={search_data}"
    try:
        response = requests.get(url)
        data = response.json()
        if "items" in data:
            search_result = data["items"][:3]
            await message.answer(f"Here your most popular links:\n"
                                 f"{search_result[0]['link']}\n"
                                 f"{search_result[1]['link']}\n"
                                 f"{search_result[2]['link']}", reply_markup=kb.main)
        else:
            await message.answer("There don't appear to be any useful results for your search.", reply_markup=kb.main)
    except Exception as e:
        await message.answer(f"An error occurred while executing the request: {e}")
    finally:
        await state.clear()


@router.message(F.text == 'Convertor')
async def set_base_cur(message: Message, state: FSMContext):
    await state.set_state(Reg.base_curr)
    await message.answer('What currency would you like to convert?\n'
                         '(UAH, USD, EUR, GBP, JPY, CNY, RUB)')


@router.message(Reg.base_curr)
async def set_curr_amount(message: Message, state: FSMContext):
    await state.update_data(base_curr=message.text)
    await state.set_state(Reg.curr_amount)
    await message.answer('Enter amount please')


@router.message(Reg.curr_amount)
async def set_target_curr(message: Message, state: FSMContext):
    await state.update_data(curr_amount=message.text)
    await state.set_state(Reg.target_curr)
    await message.answer('What is your target currency?\n'
                         '(UAH, USD, EUR, GBP, JPY, CNY, RUB)')


@router.message(Reg.target_curr)
async def exchange_rates(message: Message, state: FSMContext):
    await state.update_data(target_curr=message.text)
    convertor_data = await state.get_data()
    try:
        base_currency = convertor_data['base_curr']
        amount = convertor_data['curr_amount']
        target_currency = convertor_data['target_curr']
        url = f'https://v6.exchangerate-api.com/v6/{CONVERTOR_API}/pair/{base_currency}/{target_currency}/{amount}'
        response = requests.get(url)
        data = response.json()
        await message.answer(
            f"{amount} {base_currency.upper()} = {data['conversion_result']} {target_currency.upper()}",
            reply_markup=kb.main)
    except Exception as e:
        await message.answer("Something went wrong. Please try again", reply_markup=kb.main)
    finally:
        await state.clear()
