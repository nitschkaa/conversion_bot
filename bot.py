import asyncio
from aiogram.fsm import state
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandStart
import logging
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import httpx  # Для работы с API
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.formatting import Text

logging.basicConfig(level=logging.INFO)

bot = Bot(token='7604779913:AAEnJdFy0PHpe9nF9OD-ygM5DH7Bm1jVCj4')
dp = Dispatcher()

class CurrencyConverter(StatesGroup):
    from_currency = State()  # Исходная валюта (например, USD)
    to_currency = State()    # Целевая валюта (например, EUR)
    amount = State()         # Сумма перевода

button1 = KeyboardButton(text="USD")
button2 = KeyboardButton(text="EUR")
button3 = KeyboardButton(text="RUB")
button4 = KeyboardButton(text="GBP")

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[button1, button2, button3, button4]],  # Кнопки должны быть вложены в список списков
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('приветики пистолетики, Я - бот конвератор')

@dp.message(Command('convert'))
async def convert(message: Message, state: FSMContext):
    await message.answer('Выберете валюту из которой конвертируем', reply_markup=main_keyboard)
    await state.set_state(CurrencyConverter.from_currency) # Устанавливаем состояние "from_currency"

@dp.message(CurrencyConverter.from_currency)
async def get_convert(message: types.Message, state: FSMContext):
    await state.update_data(from_currency=message.text)
    await message.answer("Выберите валюту, в которую нужно конвертировать", reply_markup=main_keyboard)
    await state.set_state(CurrencyConverter.to_currency)  # Переходим на состояние "to_currency"

@dp.message(CurrencyConverter.to_currency)
async def conversion(message: types.Message, state: FSMContext):
    await state.update_data(to_currency=message.text)
    await message.answer("Введите сумму: ")
    await state.set_state(CurrencyConverter.amount)
#
#
@dp.message(CurrencyConverter.amount)
async def get_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)  # Преобразуем текст в число
    except ValueError:
        await message.answer("Сумма должна быть числом! Введите ещё раз:")
        return

    await state.update_data(amount=float(message.text))  # Сохраняем сумму
    data = await state.get_data()  # Получаем все введённые пользователем данные
    from_currency = data["from_currency"]
    to_currency = data["to_currency"]
    amount = data["amount"]

    # Отправляем запрос к API
    conversion_result = await convert_currency(from_currency, to_currency, amount)

    if conversion_result is None:
        await message.answer("Ошибка при получении курса валют. Попробуйте позже.")
    else:
        await message.answer(
            f"💱 Конвертация {amount} {from_currency} → {to_currency}:\n"
            f"🔹 {conversion_result:.2f} {to_currency}"
        )

    await state.clear()  # Сбрасываем состояние


async def convert_currency(from_currency: str, to_currency: str, amount: float):
    url = f"https://v6.exchangerate-api.com/v6/3be3a092e3659483327c5f86/latest/{from_currency}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    print(data)
    conversion_rates = data.get("conversion_rates", {})
    to_currency = conversion_rates.get(to_currency, None)


    return amount * to_currency  # Умножаем сумму на курс


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())