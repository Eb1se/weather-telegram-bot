"""
Модуль для создания inline-клавиатур бота.
Содержит все клавиатуры и кнопки для взаимодействия с пользователем.
"""

from aiogram.utils.keyboard import InlineKeyboardBuilder

def weather_cities_kb():
    """
    Создает главную клавиатуру с выбором городов и меню прогнозов.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками городов и навигации
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки предустановленных городов
    builder.button(text="🏙 Москва", callback_data="city_moscow")
    builder.button(text="🏙 Санкт Петербург", callback_data="city_St Petersburg")
    builder.button(text="🏙 Казань", callback_data="city_Kazan")
    builder.button(text="🏙 Калининград", callback_data="city_Kaliningrad")
    
    # Специальные кнопки
    builder.button(text="🏙 Моего города нет в списке", callback_data="other")
    builder.button(text="🗓 Меню прогнозов", callback_data="forecast")
    
    # Распределение кнопок по рядам: 2-2-1-1 (4 ряда)
    builder.adjust(2, 2, 1, 1)
    
    return builder.as_markup()

def weather_forecast_kb():
    """
    Создает клавиатуру для выбора периода прогноза погоды.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с периодами прогноза и кнопкой назад
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки выбора периода прогноза
    builder.button(text="🗓Прогноз на 3 дня", callback_data="forecast_n_3")
    builder.button(text="🗓Прогноз на 7 дней", callback_data="forecast_n_7")
    builder.button(text="🗓Прогноз на 14 дней", callback_data="forecast_n_14")
    
    # Кнопка возврата в главное меню
    builder.button(text="◀️Назад ", callback_data="back_main_menu")
    
    # Все кнопки в одном столбце (вертикальное расположение)
    builder.adjust(1)
    
    return builder.as_markup()

def weather_cities_forecast_kb():
    """
    Создает клавиатуру для выбора города при запросе прогноза погоды.
    Аналогична главной клавиатуре, но с другими callback данными и кнопкой назад.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура городов для прогноза
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки городов с префиксом forecast_city_ для обработки в прогнозах
    builder.button(text="🏙 Москва", callback_data="forecast_city_moscow")
    builder.button(text="🏙 Санкт Петербург", callback_data="forecast_city_St Petersburg")
    builder.button(text="🏙 Казань", callback_data="forecast_city_Kazan")
    builder.button(text="🏙 Калининград", callback_data="forecast_city_Kaliningrad")
    
    # Кнопка для ввода своего города (отличается callback_data от главного меню)
    builder.button(text="🏙 Моего города нет в списке", callback_data="forecast_other")
    
    # Кнопка возврата в меню выбора периода прогноза
    builder.button(text="◀️Назад ", callback_data="back_forecast_menu")
    
    # Распределение кнопок по рядам: 2-2-1-1
    builder.adjust(2, 2, 1, 1)
    
    return builder.as_markup()

def back_kb(back_to: str = "main_menu"):
    """
    Создает универсальную клавиатуру с одной кнопкой "Назад".
    
    Args:
        back_to (str): Целевое меню для возврата. 
                      Возможные значения: "main_menu", "forecast_menu", "cities_forecast_menu"
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с одной кнопкой "Назад"
    
    Examples:
        back_kb("main_menu") -> кнопка назад в главное меню
        back_kb("forecast_menu") -> кнопка назад в меню прогнозов
    """
    builder = InlineKeyboardBuilder()
    
    # Создаем кнопку "Назад" с указанием целевого меню
    # Формат callback_data: "back_{target_menu}"
    builder.button(text="◀️Назад ", callback_data=f"back_{back_to}")
    
    return builder.as_markup()