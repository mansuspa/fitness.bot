from config import TRAINING_PLANS, NUTRITION

class FitnessTrainer:
    """Fitness training logic"""
    
    @staticmethod
    def get_weekly_plan(goal: str) -> str:
        """Get weekly training plan based on goal"""
        if goal == "fat_loss":
            return (
                "🔥 НЕДЕЛЯ: ЖИРОСЖИГАНИЕ\n\n"
                "📅 ПН, СР, ПТ - Силовая тренировка (40 мин)\n"
                "🏃 ВТ, ЧТ - Кардио HIIT (25-30 мин)\n"
                "💤 СБ - Активный отдых (прогулка, йога)\n"
                "🛏️ ВС - Полный отдых\n\n"
                "⚡ Основной калорийный дефицит: 500-700 ккал"
            )
        else:  # mass
            return (
                "💪 НЕДЕЛЯ: НАБОР МАССЫ\n\n"
                "📅 PUSH/PULL/LEGS система\n"
                "🏋️ ПН - PUSH: Жим, отжимания, трицепс\n"
                "🏋️ СР - PULL: Тяги, подтягивания, бицепс\n"
                "🏋️ ПТ - LEGS: Приседания, становая, икры\n"
                "🏋️ ПП - Доп. тренировка + кардио\n\n"
                "⚡ Калорийный профицит: 300-500 ккал"
            )
    
    @staticmethod
    def get_daily_workout(goal: str, day: int = 0) -> str:
        """Get specific day workout"""
        if goal == "fat_loss":
            workouts = [
                "🏋️ НОГИ И КАРДИО\n• Приседания - 4x15 (60 сек отдыха)\n• Выпады - 3x12\n• Кардио беговая - 20 мин средний темп",
                "🏃 КАРДИО HIIT\n• Разминка - 5 мин\n• 30 сек спринт / 30 сек отдыхаx8 подходов\n• Заминка - 5 мин",
                "💪 ВЕРХ + КАРДИО\n• Жим лежа - 4x12\n• Тяга - 3x12\n• Кардио - 15 мин",
                "🧘 АКТИВНЫЙ ОТДЫХ\n• Прогулка - 30-40 мин\n• Растяжка - 15 мин\n• Мобильность суставов",
            ]
        else:  # mass
            workouts = [
                "🏋️ PUSH\n• Жим штанги - 4x8-10 (120 сек отдыха)\n• Жим гантелей - 3x10\n• Отжимания - 3x12",
                "🏋️ PULL\n• Становая тяга - 4x6-8\n• Тяга блока - 3x10\n• Подтягивания - 3x8-12",
                "🏋️ LEGS\n• Приседания - 4x8-10\n• Жим ногами - 3x10\n• Разгибание ног - 3x12",
                "💪 ДОПОВНИТЕЛЬНО\n• Бицепс - 3x10\n• Трицепс - 3x10\n• Кардио легкое - 10 мин",
            ]
        
        return workouts[day % len(workouts)]
    
    @staticmethod
    def get_nutrition_plan(goal: str) -> str:
        """Get nutrition plan"""
        plan = NUTRITION.get(goal, NUTRITION["mass"])
        
        text = f"🥗 ПЛАН ПИТАНИЯ\n\n"
        text += f"🍳 Завтрак: {plan['breakfast']}\n"
        text += f"🍽️ Обед: {plan['lunch']}\n"
        text += f"🍴 Ужин: {plan['dinner']}\n"
        text += f"🥜 Перекус: {plan['snack']}\n\n"
        text += f"💪 Белок в день: {plan['protein_daily']}\n"
        
        if goal == "mass":
            text += "🍚 Углеводы: 5-6g/kg\n💧 Жиры: 0.8-1.2g/kg"
        else:
            text += "🥬 Овощи: 300-500g\n💧 Вода: 2-3 литра"
        
        return text
    
    @staticmethod
    def calculate_calories(weight: float, height: float, age: int, gender: str, goal: str) -> dict:
        """Calculate daily calories (Mifflin-St Jeor formula)"""
        
        if gender.lower() in ["м", "male"]:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Moderate activity (3-5 days/week)
        tdee = bmr * 1.55
        
        if goal == "fat_loss":
            surplus_deficit = tdee - 500
        else:  # mass
            surplus_deficit = tdee + 400
        
        return {
            "bmr": round(bmr),
            "tdee": round(tdee),
            "daily_target": round(surplus_deficit),
            "protein": round(weight * (2.0 if goal == "mass" else 1.8)),
            "carbs": round((surplus_deficit - (weight * 2 * 4)) / 4),
        }
    
    @staticmethod
    def get_ai_advice(user_text: str, goal: str) -> str:
        """Generate AI-like advice based on user input"""
        
        text_lower = user_text.lower()
        
        # Common questions
        if any(word in text_lower for word in ["жажда", "пить", "вода"]):
            return "💧 ВОДА\nПей 2-3 литра в день! Вода ускоряет метаболизм и помогает восстановлению."
        
        if any(word in text_lower for word in ["боль", "болит"]):
            return "⚠️ БОЛЬ\nЕсли боль острая - сделай паузу. Если мышечная боль (DOMS) - это нормально!\nРастяжка + тепло помогут."
        
        if any(word in text_lower for word in ["сон", "спать"]):
            return "😴 СОН\nСпи 7-9 часов! Сон - это когда растут мышцы и идет восстановление."
        
        if any(word in text_lower for word in ["результат", "когда", "видно"]):
            if goal == "mass":
                return "📈 РЕЗУЛЬТАТЫ\n• Неделя 1: Привыкание\n• Неделя 2-3: Лучше себя чувствуешь\n• Месяц 1-2: Видны первые результаты\n• Месяц 3+: Серьезные изменения!"
            else:
                return "🔥 РЕЗУЛЬТАТЫ\n• Неделя 1-2: Энергия растет\n• Неделя 2-3: Первые 1-2 кг уходят\n• Месяц 1: Минус 3-4 кг\n• Месяц 2-3: Видны мышцы!"
        
        # Default response
        return (
            f"🤖 СОВЕТ ТРЕНЕРА\n\n"
            f"Ты спросил: '{user_text}'\n\n"
            f"💡 Рекомендация: Соблюдай план тренировок, правильно питайся и высыпайся!\n"
            f"📞 Для подробной консультации - обратись к специалисту."
        )