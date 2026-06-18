"""Nutrition database with complete meal plans and macros"""

MEALS = {
    "fat_loss": {
        "breakfast": [
            {
                "name": "Омлет из 3 яиц + цельнозерновой хлеб",
                "calories": 280,
                "protein": 18,
                "carbs": 25,
                "fats": 12,
                "description": "3 яйца + 2 ломтика цельнозернового хлеба"
            },
            {
                "name": "Овсянка с ягодами",
                "calories": 250,
                "protein": 8,
                "carbs": 45,
                "fats": 5,
                "description": "50г овсянки + 100g ягод + вода"
            },
            {
                "name": "Творог низкожирный с фруктами",
                "calories": 200,
                "protein": 25,
                "carbs": 20,
                "fats": 3,
                "description": "150g творога 0% + 1 банан"
            },
            {
                "name": "Гречка с куриным филе",
                "calories": 300,
                "protein": 30,
                "carbs": 35,
                "fats": 5,
                "description": "100g вареной гречки + 120g куриного филе"
            }
        ],
        "lunch": [
            {
                "name": "Куриная грудка с рисом и овощами",
                "calories": 450,
                "protein": 45,
                "carbs": 50,
                "fats": 8,
                "description": "150g куриной грудки + 100g риса + салат из овощей"
            },
            {
                "name": "Рыба с батаром",
                "calories": 400,
                "protein": 40,
                "carbs": 45,
                "fats": 10,
                "description": "150g рыбы + 100g сладкого картофеля + овощи"
            },
            {
                "name": "Индейка с гарниром",
                "calories": 420,
                "protein": 42,
                "carbs": 48,
                "fats": 9,
                "description": "160g индейки + 100g макарон + брокколи"
            },
            {
                "name": "Говядина с овощами",
                "calories": 480,
                "protein": 45,
                "carbs": 45,
                "fats": 15,
                "description": "140g постной говядины + картофель + морковь"
            }
        ],
        "dinner": [
            {
                "name": "Рыба на гриле с салатом",
                "calories": 350,
                "protein": 40,
                "carbs": 15,
                "fats": 12,
                "description": "180g рыбы + большой салат из овощей"
            },
            {
                "name": "Куриное филе с брокколи",
                "calories": 320,
                "protein": 42,
                "carbs": 18,
                "fats": 8,
                "description": "170g куриного филе + 200g брокколи"
            },
            {
                "name": "Запеченная индейка с овощами",
                "calories": 380,
                "protein": 44,
                "carbs": 25,
                "fats": 10,
                "description": "180g индейки + смешанные овощи"
            },
            {
                "name": "Нежирное мясо с зеленью",
                "calories": 340,
                "protein": 40,
                "carbs": 10,
                "fats": 12,
                "description": "160g постного мяса + овощи + травы"
            }
        ],
        "snack": [
            {
                "name": "Творог с ягодами",
                "calories": 150,
                "protein": 20,
                "carbs": 15,
                "fats": 2,
                "description": "100g творога 0% + 50g ягод"
            },
            {
                "name": "Яблоко с миндалем",
                "calories": 180,
                "protein": 6,
                "carbs": 25,
                "fats": 8,
                "description": "1 среднее яблоко + 15g миндаля"
            },
            {
                "name": "Протеиновый коктейль",
                "calories": 140,
                "protein": 25,
                "carbs": 8,
                "fats": 2,
                "description": "1 мерка протеина + вода"
            },
            {
                "name": "Морковь с хумусом",
                "calories": 160,
                "protein": 6,
                "carbs": 20,
                "fats": 7,
                "description": "200g моркови + 30g хумуса"
            }
        ]
    },
    "mass": {
        "breakfast": [
            {
                "name": "Омлет из 4 яиц + панир + хлеб",
                "calories": 450,
                "protein": 28,
                "carbs": 35,
                "fats": 20,
                "description": "4 яйца + 50g панира + 2 ломтика хлеба + масло"
            },
            {
                "name": "Каша гречневая с маслом",
                "calories": 480,
                "protein": 15,
                "carbs": 60,
                "fats": 18,
                "description": "100g гречки + 1 ст.л. масла + молоко"
            },
            {
                "name": "Творог жирный с медом и орехами",
                "calories": 420,
                "protein": 28,
                "carbs": 40,
                "fats": 16,
                "description": "200g творога 9% + мед + орехи + банан"
            },
            {
                "name": "Молочная каша с фруктами",
                "calories": 460,
                "protein": 18,
                "carbs": 65,
                "fats": 12,
                "description": "100g овсянки в молоке + 1 банан + 1 ст.л. масла"
            }
        ],
        "lunch": [
            {
                "name": "Курица с рисом и маслом",
                "calories": 750,
                "protein": 50,
                "carbs": 70,
                "fats": 25,
                "description": "200g куриной грудки + 150g риса + 1 ст.л. масла"
            },
            {
                "name": "Рыба с картофелем и авокадо",
                "calories": 800,
                "protein": 45,
                "carbs": 75,
                "fats": 30,
                "description": "200g рыбы + 150g картофеля + 1/2 авокадо"
            },
            {
                "name": "Постная говядина с макаронами",
                "calories": 820,
                "protein": 52,
                "carbs": 80,
                "fats": 28,
                "description": "200g говядины + 150g макарон + соус + масло"
            },
            {
                "name": "Индейка с лапшой и сливочным маслом",
                "calories": 780,
                "protein": 48,
                "carbs": 75,
                "fats": 26,
                "description": "200g индейки + 150g лапши + сливочное масло"
            }
        ],
        "dinner": [
            {
                "name": "Рыба с бататом и маслом",
                "calories": 650,
                "protein": 45,
                "carbs": 55,
                "fats": 24,
                "description": "200g рыбы + 150g батата + 1 ст.л. масла"
            },
            {
                "name": "Куриное филе с макаронами",
                "calories": 700,
                "protein": 48,
                "carbs": 70,
                "fats": 20,
                "description": "200g куриного филе + 150g макарон"
            },
            {
                "name": "Говяжий стейк с картофелем",
                "calories": 850,
                "protein": 55,
                "carbs": 65,
                "fats": 32,
                "description": "200g говяжьего стейка + 150g картофеля + масло"
            },
            {
                "name": "Запеченная индейка с гарниром",
                "calories": 720,
                "protein": 50,
                "carbs": 72,
                "fats": 22,
                "description": "220g индейки + 150g риса + овощи"
            }
        ],
        "snack": [
            {
                "name": "Творог 9% с орехами",
                "calories": 300,
                "protein": 25,
                "carbs": 20,
                "fats": 15,
                "description": "150g творога + 30g грецких орехов"
            },
            {
                "name": "Банан с арахисовым маслом",
                "calories": 320,
                "protein": 12,
                "carbs": 35,
                "fats": 16,
                "description": "1 большой банан + 2 ст.л. арахисового масла"
            },
            {
                "name": "Протеиновый коктейль с молоком",
                "calories": 350,
                "protein": 35,
                "carbs": 30,
                "fats": 10,
                "description": "2 мерки протеина + 200ml молока + банан"
            },
            {
                "name": "Сухофрукты с орехами",
                "calories": 380,
                "protein": 10,
                "carbs": 50,
                "fats": 18,
                "description": "100g сухофруктов + 40g смешанных орехов"
            }
        ]
    }
}

DAILY_TARGETS = {
    "fat_loss": {
        "description": "🔥 ПОХУДЕНИЕ",
        "calories_range": "1800-2200",
        "protein": "1.8-2.0g на kg веса",
        "carbs": "2-3g на kg веса",
        "fats": "0.5-0.8g на kg веса",
        "tips": [
            "✅ Пей 2-3 литра воды в день",
            "✅ Ешь белок при каждом приеме пищи",
            "✅ Выбирай сложные углеводы",
            "✅ Ограничивай жиры но не исключай",
            "✅ Меньше сладкого и жареного",
            "✅ Ешь медленнее, маленькими порциями"
        ]
    },
    "mass": {
        "description": "💪 НАБОР МАССЫ",
        "calories_range": "2500-3200",
        "protein": "2.0-2.2g на kg веса",
        "carbs": "5-6g на kg веса",
        "fats": "0.8-1.2g на kg веса",
        "tips": [
            "✅ Профицит калорий 300-500 ккал",
            "✅ Ешь 4-5 раз в день",
            "✅ Белок при каждом приеме пищи",
            "✅ Углеводы перед/после тренировки",
            "✅ Здоровые жиры из орехов, масла",
            "✅ Спи 8-9 часов для роста мышц"
        ]
    }
}

def format_meal(meal: dict) -> str:
    """Format meal for display"""
    text = f"🍽️ {meal['name']}\n\n"
    text += f"🔥 Калории: {meal['calories']} ккал\n"
    text += f"💪 Белки: {meal['protein']}g\n"
    text += f"🌾 Углеводы: {meal['carbs']}g\n"
    text += f"🧈 Жиры: {meal['fats']}g\n\n"
    text += f"📝 Состав: {meal['description']}\n"
    return text

def get_meal_plan(goal: str) -> str:
    """Get complete meal plan for the day"""
    if goal not in MEALS:
        return "❌ План не найден"
    
    target = DAILY_TARGETS[goal]
    text = f"{target['description']}\n\n"
    text += "="*50 + "\n\n"
    
    meals_data = MEALS[goal]
    
    text += "🍳 ЗАВТРАК (250-300 ккал):\n"
    for meal in meals_data["breakfast"][:2]:
        text += f"• {meal['name']} - {meal['calories']} ккал\n"
    
    text += "\n🍽️ ОБЕД (600-800 ккал):\n"
    for meal in meals_data["lunch"][:2]:
        text += f"• {meal['name']} - {meal['calories']} ккал\n"
    
    text += "\n🍴 УЖИН (500-700 ккал):\n"
    for meal in meals_data["dinner"][:2]:
        text += f"• {meal['name']} - {meal['calories']} ккал\n"
    
    text += "\n🥜 ПЕРЕКУС (100-300 ккал):\n"
    for meal in meals_data["snack"][:2]:
        text += f"• {meal['name']} - {meal['calories']} ккал\n"
    
    text += "\n" + "="*50 + "\n\n"
    text += f"📊 МАКРОНУТРИЕНТЫ:\n"
    text += f"💪 Белок: {target['protein']}\n"
    text += f"🌾 Углеводы: {target['carbs']}\n"
    text += f"🧈 Жиры: {target['fats']}\n"
    text += f"🔥 Калории: {target['calories_range']} ккал\n\n"
    
    text += "💡 СОВЕТЫ:\n"
    for tip in target['tips'][:4]:
        text += f"{tip}\n"
    
    return text

def get_random_meal(goal: str, meal_type: str) -> str:
    """Get random meal from specific meal type"""
    import random
    
    if goal not in MEALS or meal_type not in MEALS[goal]:
        return "❌ Не найдено"
    
    meals_list = MEALS[goal][meal_type]
    meal = random.choice(meals_list)
    return format_meal(meal)

def calculate_daily_macros(goal: str, weight: float) -> dict:
    """Calculate daily macros based on goal and weight"""
    if goal == "fat_loss":
        protein = round(weight * 2.0)
        carbs = round(weight * 2.5)
        fats = round(weight * 0.6)
        calories = round(protein * 4 + carbs * 4 + fats * 9)
    else:  # mass
        protein = round(weight * 2.1)
        carbs = round(weight * 5.5)
        fats = round(weight * 1.0)
        calories = round(protein * 4 + carbs * 4 + fats * 9)
    
    return {
        "protein": protein,
        "carbs": carbs,
        "fats": fats,
        "calories": calories
    }
