"""
Модуль обработчиков сообщений и callback'ов для телеграм бота погоды.
Содержит всю бизнес-логику взаимодействия с пользователем.
"""

from asyncio.format_helpers import _get_function_source  # TODO: Неиспользуемый импорт, можно удалить
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from app.weather_api import get_weather
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb

# Создаем главный роутер для обработчиков
router = Router()

class WeatherStates(StatesGroup):
    """
    Машина состояний (FSM) для отслеживания этапов диалога с пользователем.
    
    States:
        waiting_city: Ожидание ввода города для текущей погоды
        waiting_forecast_city: Ожидание ввода города для прогноза
    """
    waiting_city = State()
    waiting_forecast_city = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start - начальная точка взаимодействия с ботом.
    
    Args:
        message: Объект сообщения от пользователя
    """
    # Получаем имя пользователя или используем "друг" по умолчанию
    name = message.from_user.first_name or "друг" # type: ignore
    
    await message.answer(
        f"Привет {name}!\nЭто бот с помощью которого ты можешь узнать погоду!☀️",
        reply_markup=kb.weather_cities_kb()  # Показываем клавиатуру с городами
    )

@router.callback_query(F.data.startswith("back_"))
async def back_handler(callback: CallbackQuery):
    """
    Универсальный обработчик кнопок "Назад".
    Определяет куда именно нужно вернуться пользователю.
    
    Args:
        callback: Callback от inline кнопки
    """
    # Извлекаем цель возврата из callback данных (убираем префикс "back_")
    target = callback.data.replace("back_", "")# type: ignore

    # В зависимости от цели вызываем соответствующий обработчик
    if target == "main_menu":
        await back_main_menu(callback)
    elif target == "forecast_menu":
        await back_forecast_menu(callback)
    elif target == "cities_forecast_menu":
        await back_cities_forecast_menu(callback)
    
    # Подтверждаем обработку callback (убираем часики у кнопки)
    await callback.answer()
    
async def back_main_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    name = callback.from_user.first_name or "друг" # type: ignore
    await callback.message.edit_text( # type: ignore
        f"Привет {name}!\nЭто бот с помощью которого ты можешь узнать погоды!☀️",
        reply_markup=kb.weather_cities_kb()
    )

async def back_forecast_menu(callback: CallbackQuery):
    """Возврат в меню выбора периода прогноза"""
    await callback.message.edit_text(# type: ignore
        "📅 Выберите период прогноза:",
        reply_markup=kb.weather_forecast_kb()
    )
    await callback.answer()

async def back_cities_forecast_menu(callback: CallbackQuery):
    """Возврат в меню выбора города для прогноза"""
    await callback.message.edit_text(# type: ignore
        "Выберите город для прогноза:",
        reply_markup=kb.weather_cities_forecast_kb()
    )

@router.callback_query(F.data == "forecast")
async def show_forecast_menu(callback: CallbackQuery):
    """
    Обработчик перехода в меню прогнозов.
    Показывает выбор периода (3, 7, 14 дней).
    """
    await callback.message.edit_text(# type: ignore
        "📅 Выберите период прогноза:",
        reply_markup=kb.weather_forecast_kb()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("city_"))
async def city_handler(callback: CallbackQuery):
    """
    Обработчик выбора города из списка для текущей погоды.
    
    Callback data format: "city_{city_name}"
    """
    # Извлекаем название города из callback данных
    city_for_api = callback.data.replace("city_", "") # type: ignore
    
    # Получаем погоду на 1 день
    weather = await get_weather(city_for_api, 1)
    
    # Показываем погоду и кнопку возврата в главное меню
    await callback.message.edit_text(weather, reply_markup=kb.back_kb("main_menu"))  # type: ignore
    await callback.answer()

@router.callback_query(F.data == "other")
async def weather(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для случая когда города нет в списке.
    Переводит пользователя в состояние ожидания ввода города.
    """
    await callback.answer()
    
    # Просим пользователя ввести город на английском
    await callback.message.edit_text( # type: ignore
        "Напиши название своего города на <b>английском</b>:",
        parse_mode="HTML",
        reply_markup=kb.back_kb("main_menu")
    )
    
    # Сохраняем ID сообщения с запросом, чтобы потом его удалить
    await state.update_data(ask_message_id=callback.message.message_id) # type: ignore
    
    # Переводим пользователя в состояние ожидания города
    await state.set_state(WeatherStates.waiting_city)

@router.message(WeatherStates.waiting_city)
async def handle_city_input(message: Message, state: FSMContext):
    """
    Обработчик ввода города пользователем в состоянии waiting_city.
    
    Args:
        message: Сообщение с названием города
        state: Текущее состояние FSM
    """
    city = message.text
    await message.delete()  # Удаляем сообщение пользователя для чистоты чата

    # Получаем сохраненные данные из состояния
    data = await state.get_data()
    ask_message_id = data.get("ask_message_id")

    # Удаляем сообщение с запросом города (где было "Напиши название...")
    if ask_message_id:
        await message.bot.delete_message( # type: ignore
            chat_id=message.chat.id,
            message_id=ask_message_id
        )

    # Получаем и показываем погоду для введенного города
    weather = await get_weather(city, 1) # type: ignore
    await message.answer(weather, reply_markup=kb.back_kb("main_menu"))
    
    # Выходим из состояния - диалог завершен
    await state.clear()

@router.callback_query(F.data.startswith("forecast_n_"))
async def forecast_type_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора периода прогноза (3, 7, 14 дней).
    
    Callback data format: "forecast_n_{days}"
    """
    # Извлекаем количество дней из callback данных
    days = int(callback.data.replace("forecast_n_", "")) # type: ignore

    # Сохраняем выбранное количество дней в состоянии
    await state.update_data(forecast_days=days)
    
    # Переходим в состояние ожидания выбора города для прогноза
    await state.set_state(WeatherStates.waiting_forecast_city)
    
    # Формируем правильное окончание для слова "день"
    days_text = "дня" if days == 3 else "дней"

    await callback.message.edit_text( # type: ignore
        f"Выбери город для прогноза на {days} {days_text}",
        reply_markup=kb.weather_cities_forecast_kb()
    )
    await callback.answer()

@router.callback_query(F.data == "forecast_other")
async def forecast_other_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для ввода своего города при выборе прогноза.
    """
    await callback.answer()

    # Получаем сохраненное количество дней из состояния
    data = await state.get_data()
    days = data.get("forecast_days")
    days_text = "дня" if days == 3 else "дней"

    await callback.message.edit_text( # type: ignore
        f"Напиши название вашего на <b>английском</b> города для прогноза на {days} {days_text}",
        parse_mode="HTML",
        reply_markup=kb.back_kb("cities_forecast_menu")
    )
    
    # Сохраняем ID сообщения с запросом для последующего удаления
    await state.update_data(ask_message_id=callback.message.message_id) # type: ignore

@router.message(WeatherStates.waiting_forecast_city)
async def handle_forecast_city_input(message: Message, state: FSMContext):
    """
    Обработчик ввода города для прогноза в состоянии waiting_forecast_city.
    """
    city = message.text
    await message.delete()  # Удаляем сообщение пользователя

    # Получаем все данные из состояния
    data = await state.get_data()
    ask_message_id = data.get("ask_message_id")
    days = data.get("forecast_days")

    # Удаляем сообщение с запросом города
    if ask_message_id:
        await message.bot.delete_message( # type: ignore
            chat_id=message.chat.id,
            message_id=ask_message_id
        )

    # Получаем прогноз и показываем результат
    forecast = await get_weather(city, days) # type: ignore
    await message.answer(forecast, reply_markup=kb.back_kb("forecast_menu"))
    
    # Завершаем диалог - очищаем состояние
    await state.clear()

@router.callback_query(F.data.startswith("forecast_city_"), WeatherStates.waiting_forecast_city)
async def forecast_city_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора города из списка для прогноза погоды.
    
    Callback data format: "forecast_city_{city_name}"
    """
    # Извлекаем название города из callback данных
    city_for_api = callback.data.replace("forecast_city_", "")# type: ignore

    # Получаем сохраненное количество дней из состояния
    data = await state.get_data()
    days = data.get("forecast_days")

    # Получаем прогноз погоды
    forecast = await get_weather(city_for_api, days) # type: ignore

    # Показываем прогноз и кнопку возврата в меню прогнозов
    await callback.message.edit_text(forecast, reply_markup=kb.back_kb("forecast_menu")) # type: ignore
    
    # Завершаем диалог - очищаем состояние FSM
    await state.clear()
    await callback.answer()