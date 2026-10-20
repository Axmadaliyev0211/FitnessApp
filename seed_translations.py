"""
FitnesApp — Tarjima Seed Scripti
Barcha modellarning _uz va _ru fieldlarini to'ldiradi.
Ishlatish: python seed_translations.py
"""

import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from workouts.models import WorkoutCategory, Workout, Exercise
from nutrition.models import Recipe
from support.models import FAQ
from content.models import Article
from community.models import Challenge, ForumCategory, ForumPost
from users.models import UserGoal

print("=" * 60)
print("  TARJIMA SEED BOSHLANDI")
print("=" * 60)

# ─────────────────────────────────────────────
# 1. WorkoutCategory
# ─────────────────────────────────────────────
print("\n[1] WorkoutCategory tarjimalari...")

cat_translations = {
    # id: (name_uz, name_en, name_ru)
    1: ("Test kategoriya", "Test Category",      "Тестовая категория"),
    2: ("Test",            "Test",               "Тест"),
    3: ("Cat27",           "Cat27",              "Cat27"),
    4: ("Kardio",          "Cardio",             "Кардио"),
    5: ("Kuch mashqlari",  "Strength",           "Силовые тренировки"),
    6: ("Yoga",            "Yoga",               "Йога"),
}

for cat_id, (uz, en, ru) in cat_translations.items():
    updated = WorkoutCategory.objects.filter(id=cat_id).update(
        name_uz=uz, name_en=en, name_ru=ru
    )
    if updated:
        print(f"  ✓ id={cat_id}: uz='{uz}' | en='{en}' | ru='{ru}'")

# ─────────────────────────────────────────────
# 2. Workout
# ─────────────────────────────────────────────
print("\n[2] Workout tarjimalari...")

from workouts.models import Workout

workout_translations = {
    "Morning Yoga Flow": {
        "title_uz": "Ertalabki Yoga",
        "title_en": "Morning Yoga Flow",
        "title_ru": "Утренняя йога",
        "description_uz": "Tanani uyg'otadigan yumshoq yoga harakatlari to'plami.",
        "description_en": "A gentle yoga sequence to wake up your body.",
        "description_ru": "Мягкая последовательность йоги для пробуждения тела.",
    },
    "Advanced Strength Program": {
        "title_uz": "Ilg'or Kuch Dasturi",
        "title_en": "Advanced Strength Program",
        "title_ru": "Продвинутая силовая программа",
        "description_uz": "Tajribali sportchilar uchun og'ir kuch mashqlari.",
        "description_en": "Heavy strength exercises for experienced athletes.",
        "description_ru": "Тяжёлые силовые упражнения для опытных спортсменов.",
    },
    "Beginner Full Body": {
        "title_uz": "Boshlang'ich To'liq Tana",
        "title_en": "Beginner Full Body",
        "title_ru": "Тренировка всего тела для начинающих",
        "description_uz": "Yangi boshlovchilar uchun to'liq tana mashqlari.",
        "description_en": "Full body workout designed for beginners.",
        "description_ru": "Тренировка всего тела для начинающих.",
    },
}

for obj in Workout.objects.all():
    key = obj.title_en or obj.title_uz or obj.title
    if key in workout_translations:
        t = workout_translations[key]
        for field, val in t.items():
            setattr(obj, field, val)
        obj.save()
        print(f"  ✓ '{key}' → uz/en/ru tarjima saqlandi")
    else:
        # noma'lum workout — asosiy title ni barcha tillarga ko'chiramiz
        base = obj.title_en or obj.title_uz or obj.title or ""
        obj.title_uz = obj.title_uz or base
        obj.title_en = obj.title_en or base
        obj.title_ru = obj.title_ru or base
        obj.description_uz = obj.description_uz or obj.description or ""
        obj.description_en = obj.description_en or obj.description or ""
        obj.description_ru = obj.description_ru or obj.description or ""
        obj.save()
        print(f"  ~ id={obj.id}: fallback bilan saqlandi")

# ─────────────────────────────────────────────
# 3. Exercise
# ─────────────────────────────────────────────
print("\n[3] Exercise tarjimalari...")

exercise_translations = {
    "Push Up": {
        "name_uz": "Yerdan bosish",
        "name_en": "Push Up",
        "name_ru": "Отжимание",
        "description_uz": "Ko'krak va triseps mushaklarini ishlatadiganasosiy mashq.",
        "description_en": "A basic exercise that works the chest and triceps.",
        "description_ru": "Базовое упражнение для грудных мышц и трицепса.",
    },
    "Squat": {
        "name_uz": "Cho'kish (Squat)",
        "name_en": "Squat",
        "name_ru": "Приседание",
        "description_uz": "Son va dumba mushaklarini rivojlantiruvchi mashq.",
        "description_en": "Exercise that develops quadriceps and glute muscles.",
        "description_ru": "Упражнение для развития квадрицепсов и ягодичных мышц.",
    },
    "Deadlift": {
        "name_uz": "Og'irlik ko'tarish (Deadlift)",
        "name_en": "Deadlift",
        "name_ru": "Становая тяга",
        "description_uz": "Orqa va tizza osti mushaklarini kuchaytiradigan mashq.",
        "description_en": "A compound exercise strengthening the back and hamstrings.",
        "description_ru": "Комплексное упражнение для спины и задней поверхности бедра.",
    },
    "Pull Up": {
        "name_uz": "Turnikda tortilish",
        "name_en": "Pull Up",
        "name_ru": "Подтягивание",
        "description_uz": "Orqa va bitseps mushaklarini rivojlantiruvchi mashq.",
        "description_en": "Exercise that develops the back and biceps muscles.",
        "description_ru": "Упражнение для развития мышц спины и бицепса.",
    },
    "Plank": {
        "name_uz": "Taxtacha (Plank)",
        "name_en": "Plank",
        "name_ru": "Планка",
        "description_uz": "Qorin va yadro mushaklarini mustahkamlovchi statik mashq.",
        "description_en": "A static exercise that strengthens the core and abdominal muscles.",
        "description_ru": "Статическое упражнение для укрепления мышц кора и пресса.",
    },
}

for obj in Exercise.objects.all():
    key = obj.name_en or obj.name
    if key in exercise_translations:
        t = exercise_translations[key]
        for field, val in t.items():
            setattr(obj, field, val)
        obj.save()
        print(f"  ✓ '{key}' → uz/en/ru saqlandi")

# ─────────────────────────────────────────────
# 4. Recipe
# ─────────────────────────────────────────────
print("\n[4] Recipe tarjimalari...")

recipe_translations = {
    "Tarvuz smoothie": {
        "title_uz": "Tarvuz smoothie",
        "title_en": "Watermelon Smoothie",
        "title_ru": "Арбузный смузи",
        "description_uz": "Yangilantiruvchi tarvuz va yogurt bilan tayyorlangan foydali ichimlik.",
        "description_en": "A refreshing healthy drink made with watermelon and yogurt.",
        "description_ru": "Освежающий полезный напиток из арбуза и йогурта.",
        "preparation_steps_uz": "1. Tarvuzni maydalang. 2. Yogurt bilan aralashtiring. 3. Muzlatgichda sovuting.",
        "preparation_steps_en": "1. Blend watermelon. 2. Mix with yogurt. 3. Serve chilled.",
        "preparation_steps_ru": "1. Измельчите арбуз. 2. Смешайте с йогуртом. 3. Подавайте охлаждённым.",
    },
    "Tovuq ko'krak salatasi": {
        "title_uz": "Tovuq ko'krak salatasi",
        "title_en": "Chicken Breast Salad",
        "title_ru": "Салат из куриной грудки",
        "description_uz": "Oqsillarga boy tovuq ko'krak go'shti va yangi sabzavotlar salatasi.",
        "description_en": "A protein-rich salad made with chicken breast and fresh vegetables.",
        "description_ru": "Богатый белком салат из куриной грудки и свежих овощей.",
        "preparation_steps_uz": "1. Tovuqni qaynatib maydalang. 2. Sabzavotlar bilan aralashtiring. 3. Ziravor soling.",
        "preparation_steps_en": "1. Boil and shred the chicken. 2. Mix with vegetables. 3. Season to taste.",
        "preparation_steps_ru": "1. Отварите и измельчите курицу. 2. Смешайте с овощами. 3. Приправьте по вкусу.",
    },
    "Oqshom sho'rvasi": {
        "title_uz": "Oqshom sho'rvasi",
        "title_en": "Evening Soup",
        "title_ru": "Вечерний суп",
        "description_uz": "Ovqat hazm qilishni yaxshilovchi yengil sabzavotli sho'rva.",
        "description_en": "A light vegetable soup that aids digestion.",
        "description_ru": "Лёгкий овощной суп, улучшающий пищеварение.",
        "preparation_steps_uz": "1. Sabzavotlarni toza suvda qaynatib oling. 2. Go'sht qo'shing. 3. 30 daqiqa qaynatib damsing.",
        "preparation_steps_en": "1. Boil vegetables in clean water. 2. Add meat. 3. Simmer for 30 minutes.",
        "preparation_steps_ru": "1. Отварите овощи в чистой воде. 2. Добавьте мясо. 3. Тушите 30 минут.",
    },
}

for obj in Recipe.objects.all():
    key = obj.title_en or obj.title
    if key in recipe_translations:
        t = recipe_translations[key]
        for field, val in t.items():
            setattr(obj, field, val)
        obj.save()
        print(f"  ✓ '{key}' → uz/en/ru saqlandi")

# ─────────────────────────────────────────────
# 5. FAQ
# ─────────────────────────────────────────────
print("\n[5] FAQ tarjimalari...")

faq_translations = {
    "Parolimni qanday o'zgartirsam bo'ladi?": {
        "question_uz": "Parolimni qanday o'zgartirsam bo'ladi?",
        "question_en": "How can I change my password?",
        "question_ru": "Как изменить пароль?",
        "answer_uz": "Profil > Sozlamalar > Parolni o'zgartirish bo'limiga o'ting.",
        "answer_en": "Go to Profile > Settings > Change Password.",
        "answer_ru": "Перейдите в Профиль > Настройки > Изменить пароль.",
    },
    "Premium obuna qanday ishlaydi?": {
        "question_uz": "Premium obuna qanday ishlaydi?",
        "question_en": "How does the premium subscription work?",
        "question_ru": "Как работает премиум-подписка?",
        "answer_uz": "Premium obuna barcha mashq va ovqatlanish rejalarini ochadi.",
        "answer_en": "Premium subscription unlocks all workout and nutrition plans.",
        "answer_ru": "Премиум-подписка открывает все тренировки и планы питания.",
    },
    "Kaloriya hisobi qanday amalga oshiriladi?": {
        "question_uz": "Kaloriya hisobi qanday amalga oshiriladi?",
        "question_en": "How is calorie counting done?",
        "question_ru": "Как ведётся подсчёт калорий?",
        "answer_uz": "Har bir mashq uchun sarflangan kaloriya avtomatik hisoblanadi.",
        "answer_en": "Calories burned are automatically calculated for each workout.",
        "answer_ru": "Сожжённые калории автоматически рассчитываются для каждой тренировки.",
    },
}

for obj in FAQ.objects.all():
    key = obj.question_en or obj.question
    if key in faq_translations:
        t = faq_translations[key]
        for field, val in t.items():
            setattr(obj, field, val)
        obj.save()
        print(f"  ✓ '{key[:40]}' → uz/en/ru saqlandi")

# ─────────────────────────────────────────────
# 6. Article
# ─────────────────────────────────────────────
print("\n[6] Article tarjimalari...")

article_translations = {
    "Motivatsiya: Maqsadga Etish Sirlari": {
        "title_uz": "Motivatsiya: Maqsadga Etish Sirlari",
        "title_en": "Motivation: Secrets to Achieving Your Goals",
        "title_ru": "Мотивация: Секреты достижения целей",
        "content_uz": "Muvaffaqiyatga erishish uchun muntazamlik va intizom asosiy omillardir. Har kuni kichik qadamlar qo'yish, o'z natijalarini kuzatib borish va salbiy fikrlardan uzoq turish muhimdir.",
        "content_en": "Consistency and discipline are the key factors for success. Taking small steps every day, tracking your results, and staying away from negative thoughts are essential.",
        "content_ru": "Последовательность и дисциплина — ключевые факторы успеха. Делать небольшие шаги каждый день, отслеживать результаты и избегать негативных мыслей — это важно.",
    },
    "10 ta Eng Yaxshi Protein Manbalar": {
        "title_uz": "10 ta Eng Yaxshi Protein Manbalar",
        "title_en": "Top 10 Best Protein Sources",
        "title_ru": "10 лучших источников белка",
        "content_uz": "Protein ovqatlanishda juda muhim rol o'ynaydi. Eng yaxshi manbalar: tuxum, tovuq go'shti, baliq, paxta yog'i, loviya va boshqalar.",
        "content_en": "Protein plays a very important role in nutrition. The best sources include eggs, chicken, fish, cottage cheese, beans, and more.",
        "content_ru": "Белок играет очень важную роль в питании. Лучшие источники: яйца, курица, рыба, творог, бобовые и другие.",
    },
    "Beginner uchun Squat Texnikasi": {
        "title_uz": "Boshlang'ichlar uchun Squat Texnikasi",
        "title_en": "Squat Technique for Beginners",
        "title_ru": "Техника приседаний для начинающих",
        "content_uz": "Squat — eng asosiy mashqlardan biri. To'g'ri texnika jarohatlanishning oldini oladi. Oyoqlarni yelka kengligida qo'ying, tizza avval bukilsin.",
        "content_en": "Squat is one of the most fundamental exercises. Proper technique prevents injuries. Place your feet shoulder-width apart and bend your knees first.",
        "content_ru": "Приседание — одно из самых базовых упражнений. Правильная техника предотвращает травмы. Поставьте ноги на ширину плеч, сначала сгибайте колени.",
    },
}

for obj in Article.objects.all():
    key = obj.title_en or obj.title
    if key in article_translations:
        t = article_translations[key]
        for field, val in t.items():
            setattr(obj, field, val)
        obj.save()
        print(f"  ✓ '{key[:40]}' → uz/en/ru saqlandi")

# ─────────────────────────────────────────────
# 7. Challenge
# ─────────────────────────────────────────────
print("\n[7] Challenge tarjimalari...")

challenge_translations = {
    "30 kunlik Squat Challenge": {
        "title_uz": "30 kunlik Squat Challenge",
        "title_en": "30-Day Squat Challenge",
        "title_ru": "30-дневный челлендж приседаний",
        "description_uz": "Har kuni squat bajaring va 30 kunda natijaga erishing!",
        "description_en": "Do squats every day and achieve results in 30 days!",
        "description_ru": "Делайте приседания каждый день и добивайтесь результатов за 30 дней!",
    },
    "Haftalik Cardio Challenge": {
        "title_uz": "Haftalik Kardio Challenge",
        "title_en": "Weekly Cardio Challenge",
        "title_ru": "Еженедельный кардио-челлендж",
        "description_uz": "Bu hafta maksimal kardio yuklamasi bilan chidamliligingizni oshiring.",
        "description_en": "Boost your endurance with maximum cardio load this week.",
        "description_ru": "Повысьте свою выносливость с максимальной кардионагрузкой на этой неделе.",
    },
    "Core Strength Challenge": {
        "title_uz": "Yadro Kuchi Challenge",
        "title_en": "Core Strength Challenge",
        "title_ru": "Челлендж силы кора",
        "description_uz": "Qorin va bel mushaklaringizni 14 kunda kuchlaytiring.",
        "description_en": "Strengthen your core and lower back muscles in 14 days.",
        "description_ru": "Укрепите мышцы кора и поясницы за 14 дней.",
    },
}

for obj in Challenge.objects.all():
    key = obj.title_en or obj.title_uz or obj.title
    if key in challenge_translations:
        t = challenge_translations[key]
        for field, val in t.items():
            setattr(obj, field, val)
        obj.save()
        print(f"  ✓ '{key[:40]}' → uz/en/ru saqlandi")
    else:
        # noma'lum — mavjud qiymatni barcha tillarga ko'chir
        base_title = obj.title_uz or obj.title_en or obj.title or ""
        base_desc  = obj.description_uz or obj.description_en or obj.description or ""
        obj.title_uz = obj.title_uz or base_title
        obj.title_en = obj.title_en or base_title
        obj.title_ru = obj.title_ru or base_title
        obj.description_uz = obj.description_uz or base_desc
        obj.description_en = obj.description_en or base_desc
        obj.description_ru = obj.description_ru or base_desc
        obj.save()
        print(f"  ~ id={obj.id} '{base_title[:30]}': fallback bilan saqlandi")

# ─────────────────────────────────────────────
# 8. ForumCategory
# ─────────────────────────────────────────────
print("\n[8] ForumCategory tarjimalari...")

forum_cat_translations = {
    "Umumiy":       ("Umumiy",      "General",    "Общее"),
    "Mashqlar":     ("Mashqlar",    "Workouts",   "Тренировки"),
    "Ovqatlanish":  ("Ovqatlanish", "Nutrition",  "Питание"),
    "Tez ozish":    ("Tez ozish",   "Quick Loss", "Быстрое похудение"),
    "TestCat":      ("Test",        "TestCat",    "Тест"),
}

for obj in ForumCategory.objects.all():
    key = obj.name_uz or obj.name
    if key in forum_cat_translations:
        uz, en, ru = forum_cat_translations[key]
        obj.name_uz = uz
        obj.name_en = en
        obj.name_ru = ru
        obj.save()
        print(f"  ✓ '{key}' → uz='{uz}' en='{en}' ru='{ru}'")
    else:
        base = obj.name or ""
        obj.name_uz = obj.name_uz or base
        obj.name_en = obj.name_en or base
        obj.name_ru = obj.name_ru or base
        obj.save()
        print(f"  ~ id={obj.id} '{base}': fallback saqlandi")

# ─────────────────────────────────────────────
# 9. ForumPost
# ─────────────────────────────────────────────
print("\n[9] ForumPost tarjimalari...")

post_translations = {
    "Birinchi mashqim haqida": {
        "title_uz": "Birinchi mashqim haqida",
        "title_en": "About My First Workout",
        "title_ru": "О моей первой тренировке",
        "content_uz": "Bugun birinchi mashqimni bajardim, juda zo'r edi! Charchadim lekin natija ajoyib.",
        "content_en": "Today I completed my first workout, it was amazing! I was tired but the result was great.",
        "content_ru": "Сегодня я завершил свою первую тренировку, это было потрясающе! Устал, но результат отличный.",
    },
    "Push-up texnikasi": {
        "title_uz": "Push-up texnikasi",
        "title_en": "Push-up Technique",
        "title_ru": "Техника отжиманий",
        "content_uz": "Push-up to'g'ri qilish uchun qanday maslahat bor? Bel to'g'ri turishi kerakmi?",
        "content_en": "Any tips for proper push-up form? Should the back stay straight?",
        "content_ru": "Есть ли советы по правильной технике отжиманий? Должна ли спина быть прямой?",
    },
    "Protein qabuli": {
        "title_uz": "Protein qabuli",
        "title_en": "Protein Intake",
        "title_ru": "Потребление белка",
        "content_uz": "Kuniga necha gramm protein iste'mol qilish kerak? Tana vazniga nisbatan hisoblanadimi?",
        "content_en": "How many grams of protein should I consume daily? Is it calculated based on body weight?",
        "content_ru": "Сколько граммов белка нужно употреблять в день? Рассчитывается ли это на основе веса тела?",
    },
}

for obj in ForumPost.objects.all():
    key = obj.title_en or obj.title_uz or obj.title
    if key in post_translations:
        t = post_translations[key]
        for field, val in t.items():
            setattr(obj, field, val)
        obj.save()
        print(f"  ✓ '{key[:40]}' → uz/en/ru saqlandi")
    else:
        base_t = obj.title or ""
        base_c = obj.content or ""
        obj.title_uz = obj.title_uz or base_t
        obj.title_en = obj.title_en or base_t
        obj.title_ru = obj.title_ru or base_t
        obj.content_uz = obj.content_uz or base_c
        obj.content_en = obj.content_en or base_c
        obj.content_ru = obj.content_ru or base_c
        obj.save()
        print(f"  ~ id={obj.id} '{base_t[:30]}': fallback saqlandi")

# ─────────────────────────────────────────────
# 10. UserGoal
# ─────────────────────────────────────────────
print("\n[10] UserGoal tarjimalari...")

goal_translations = {
    "Vazn yo'qtirish":  ("Vazn yo'qtirish", "Lose Weight",       "Похудение"),
    "Mushak oshirish":  ("Mushak oshirish", "Build Muscle",      "Набор мышечной массы"),
    "Test Maqsad":      ("Test Maqsad",     "Test Goal",         "Тестовая цель"),
    "Yangi Maqsad":     ("Yangi Maqsad",    "New Goal",          "Новая цель"),
}

for obj in UserGoal.objects.all():
    key = obj.title_en or obj.title_uz or obj.title
    if key and key in goal_translations:
        uz, en, ru = goal_translations[key]
        obj.title_uz = uz
        obj.title_en = en
        obj.title_ru = ru
        obj.save()
        print(f"  ✓ '{key}' → uz/en/ru saqlandi")
    else:
        base = obj.title_en or obj.title_uz or obj.title or ""
        obj.title_uz = obj.title_uz or base
        obj.title_en = obj.title_en or base
        obj.title_ru = obj.title_ru or base
        obj.save()
        print(f"  ~ id={obj.id} '{base}': fallback saqlandi")

# ─────────────────────────────────────────────
# YAKUNIY NATIJA
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  TARJIMA SEED YAKUNLANDI — Nazorat tekshiruvi:")
print("=" * 60)

from django.utils import translation

checks = [
    ("WorkoutCategory", WorkoutCategory, "name"),
    ("Workout",         Workout,         "title"),
    ("Exercise",        Exercise,        "name"),
    ("Recipe",          Recipe,          "title"),
    ("FAQ",             FAQ,             "question"),
    ("Article",         Article,         "title"),
    ("Challenge",       Challenge,       "title"),
    ("ForumCategory",   ForumCategory,   "name"),
    ("ForumPost",       ForumPost,       "title"),
    ("UserGoal",        UserGoal,        "title"),
]

print(f"\n  {'Model':<18} {'UZ':>6} {'EN':>6} {'RU':>6}  {'Jami':>6}")
print("  " + "-" * 46)
for model_name, Model, field in checks:
    total = Model.objects.count()
    uz = Model.objects.exclude(**{f"{field}_uz__isnull": True}).exclude(**{f"{field}_uz__exact": ""}).count()
    en = Model.objects.exclude(**{f"{field}_en__isnull": True}).exclude(**{f"{field}_en__exact": ""}).count()
    ru = Model.objects.exclude(**{f"{field}_ru__isnull": True}).exclude(**{f"{field}_ru__exact": ""}).count()
    uz_s = f"{uz}/{total}"
    en_s = f"{en}/{total}"
    ru_s = f"{ru}/{total}"
    print(f"  {model_name:<18} {uz_s:>6} {en_s:>6} {ru_s:>6}")

print("\n  Tarjima seed muvaffaqiyatli yakunlandi!")
print("=" * 60)
