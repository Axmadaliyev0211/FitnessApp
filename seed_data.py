"""
FitnesApp - To'liq Seed Script
Barcha modellar uchun test ma'lumotlar yaratadi.
Ishlatish: python seed_data.py
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
from django.utils import timezone

# Django sozlamalari
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# --- Import models ---
from django.contrib.auth import get_user_model
from workouts.models import (
    WorkoutCategory, Exercise, Workout, WorkoutExercise,
    CustomRoutine, CustomRoutineExercise, UserWorkoutLog, ExerciseLog, FavoriteWorkout
)
from nutrition.models import Recipe, MealPlanPreference, GeneratedMealPlan, MealLog, FavoriteRecipe
from progress.models import ProgressEntry, ActivityLog
from community.models import (
    ForumCategory, ForumPost, ForumComment, PostLike,
    Challenge, ChallengeRound, ChallengeExercise, UserChallenge
)
from content.models import Article, FavoriteArticle
from notifications.models import Notification
from support.models import FAQ, SupportMessage
from users.models import UserGoal, UserSettings

User = get_user_model()

print("=" * 60)
print("  FitnesApp SEED SCRIPT boshlandi")
print("=" * 60)

# ==================================================
# 1. FOYDALANUVCHILAR
# ==================================================
print("\n[1/15] Foydalanuvchilar yaratilmoqda...")

def create_user(username, email, password, full_name, is_trainer=False, is_premium=False, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'full_name': full_name,
            'nickname': username,
            'is_trainer': is_trainer,
            'is_premium': is_premium,
            'is_staff': is_staff,
            'gender': 'male',
            'date_of_birth': date(1995, 6, 15),
            'height_cm': 175.0,
            'weight_kg': 75.0,
            'fitness_level': 'intermediate',
            'primary_goal': 'muscle_mass_gain',
        }
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"  ✓ Yangi user: {email}")
    else:
        print(f"  ~ Mavjud user: {email}")
    return user

user1 = create_user('user1', 'user1@test.com', 'Test12345!', 'Test User One')
user2 = create_user('user2', 'user2@test.com', 'Test12345!', 'Test User Two')
trainer = create_user('trainer', 'trainer@test.com', 'Test12345!', 'Pro Trainer', is_trainer=True)

# UserSettings
for u in [user1, user2, trainer]:
    UserSettings.objects.get_or_create(
        user=u,
        defaults={
            'notifications_enabled': True,
            'sound_enabled': True,
            'reminder_enabled': True,
        }
    )
print(f"  ✓ UserSettings: 3 ta")

# UserGoal
goals_created = 0
for u in [user1, user2]:
    goal, created = UserGoal.objects.get_or_create(
        user=u,
        goal_type='lose_weight',
        defaults={
            'title': 'Vazn yo\'qtirish',
            'target_value': 70.0,
            'current_value': 75.0,
            'unit': 'kg',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=90),
            'status': 'active',
        }
    )
    if created:
        goals_created += 1
    goal2, created2 = UserGoal.objects.get_or_create(
        user=u,
        goal_type='muscle_mass_gain',
        defaults={
            'title': 'Mushak oshirish',
            'target_value': 10.0,
            'current_value': 2.0,
            'unit': 'kg',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=120),
            'status': 'active',
        }
    )
    if created2:
        goals_created += 1
print(f"  ✓ UserGoal: {goals_created} yangi yaratildi")

# ==================================================
# 2. WORKOUT CATEGORIES
# ==================================================
print("\n[2/15] WorkoutCategory yaratilmoqda...")
categories_data = [
    {'name': 'Cardio', 'slug': 'cardio', 'icon': 'running', 'order': 1},
    {'name': 'Strength', 'slug': 'strength', 'icon': 'dumbbell', 'order': 2},
    {'name': 'Yoga', 'slug': 'yoga', 'icon': 'yoga', 'order': 3},
]
cats = []
for cd in categories_data:
    obj, created = WorkoutCategory.objects.get_or_create(slug=cd['slug'], defaults=cd)
    cats.append(obj)
print(f"  ✓ WorkoutCategory: {len(cats)} ta")

# ==================================================
# 3. EXERCISES
# ==================================================
print("\n[3/15] Exercise yaratilmoqda...")
exercises_data = [
    {'name': 'Push Up', 'difficulty_level': 'beginner', 'muscle_group': ['chest', 'triceps'], 'equipment': [], 'instructions': '1. Yotib ol. 2. Ko\'tar.'},
    {'name': 'Squat', 'difficulty_level': 'beginner', 'muscle_group': ['quads', 'glutes'], 'equipment': [], 'instructions': '1. Tik tur. 2. O\'tir.'},
    {'name': 'Deadlift', 'difficulty_level': 'intermediate', 'muscle_group': ['back', 'hamstrings'], 'equipment': ['barbell'], 'instructions': '1. Og\'irlikni ko\'tar.'},
    {'name': 'Pull Up', 'difficulty_level': 'intermediate', 'muscle_group': ['back', 'biceps'], 'equipment': ['pull-up bar'], 'instructions': '1. Osil. 2. Ko\'tar.'},
    {'name': 'Plank', 'difficulty_level': 'beginner', 'muscle_group': ['core'], 'equipment': [], 'instructions': '1. Taxtadek yot.'},
]
exercises = []
for ed in exercises_data:
    obj, created = Exercise.objects.get_or_create(name=ed['name'], defaults=ed)
    exercises.append(obj)
print(f"  ✓ Exercise: {len(exercises)} ta")

# ==================================================
# 4. WORKOUTS
# ==================================================
print("\n[4/15] Workout yaratilmoqda...")
workouts_data = [
    {
        'title': 'Beginner Full Body',
        'difficulty_level': 'beginner',
        'duration_minutes': 30,
        'calories_estimated': 200,
        'is_premium': False,
        'is_training_of_the_day': True,
        'category': cats[0],
        'created_by': trainer,
    },
    {
        'title': 'Advanced Strength Program',
        'difficulty_level': 'advanced',
        'duration_minutes': 60,
        'calories_estimated': 500,
        'is_premium': True,
        'is_training_of_the_day': False,
        'category': cats[1],
        'created_by': trainer,
    },
    {
        'title': 'Morning Yoga Flow',
        'difficulty_level': 'beginner',
        'duration_minutes': 20,
        'calories_estimated': 100,
        'is_premium': False,
        'is_training_of_the_day': False,
        'category': cats[2],
        'created_by': trainer,
    },
]
workouts = []
for wd in workouts_data:
    obj, created = Workout.objects.get_or_create(title=wd['title'], defaults=wd)
    workouts.append(obj)
print(f"  ✓ Workout: {len(workouts)} ta (1 training_of_the_day, 1 premium, 1 oddiy)")

# WorkoutExercise
we_count = 0
for i, ex in enumerate(exercises[:3]):
    obj, created = WorkoutExercise.objects.get_or_create(
        workout=workouts[0], exercise=ex,
        defaults={'sets': 3, 'reps': 10, 'rest_seconds': 60, 'order': i}
    )
    if created:
        we_count += 1
print(f"  ✓ WorkoutExercise: {we_count} yangi")

# ==================================================
# 5. CUSTOM ROUTINES
# ==================================================
print("\n[5/15] CustomRoutine yaratilmoqda...")
cr_count = 0
for u in [user1, user2]:
    obj, created = CustomRoutine.objects.get_or_create(
        user=u, title=f'{u.nickname} - Shaxsiy mashq',
        defaults={}
    )
    if created:
        cr_count += 1
        # CustomRoutineExercise qo'shish
        for i, ex in enumerate(exercises[:2]):
            CustomRoutineExercise.objects.get_or_create(
                custom_routine=obj, exercise=ex,
                defaults={'sets': 3, 'reps': 12, 'order': i, 'round_number': 1}
            )
print(f"  ✓ CustomRoutine: {cr_count} yangi")

# ==================================================
# 6. WORKOUT LOGS
# ==================================================
print("\n[6/15] UserWorkoutLog & ExerciseLog yaratilmoqda...")
log_count = 0
for u in [user1, user2]:
    log, created = UserWorkoutLog.objects.get_or_create(
        user=u,
        workout=workouts[0],
        started_at=timezone.now() - timedelta(hours=2),
        defaults={
            'completed_at': timezone.now() - timedelta(hours=1),
            'duration_seconds': 3600,
            'calories_burned': 250.0,
            'rating': 4,
            'notes': 'Yaxshi mashq!',
        }
    )
    if created:
        log_count += 1
        # ExerciseLog
        for ex in exercises[:2]:
            ExerciseLog.objects.get_or_create(
                user_workout_log=log,
                exercise=ex,
                defaults={
                    'sets_number': 3,
                    'reps': 10,
                    'weight_used': 20.0,
                    'completed': True
                }
            )
print(f"  ✓ UserWorkoutLog: {log_count} yangi (ExerciseLog ham qo'shildi)")

# ==================================================
# 7. FAVORITE WORKOUTS
# ==================================================
print("\n[7/15] FavoriteWorkout yaratilmoqda...")
fav_w_count = 0
for u in [user1, user2]:
    obj, created = FavoriteWorkout.objects.get_or_create(user=u, workout=workouts[0])
    if created:
        fav_w_count += 1
print(f"  ✓ FavoriteWorkout: {fav_w_count} yangi")

# ==================================================
# 8. RECIPES
# ==================================================
print("\n[8/15] Recipe yaratilmoqda...")
recipes_data = [
    {
        'title': 'Tarvuz smoothie',
        'calories': 150,
        'protein': 3.0,
        'carbs': 30.0,
        'fat': 1.0,
        'meal_type': 'breakfast',
        'prep_time_minutes': 5,
        'ingredients': [{'name': 'tarvuz', 'amount': '200g'}, {'name': 'yogurt', 'amount': '100ml'}],
        'is_recipe_of_the_day': True,
    },
    {
        'title': 'Tovuq ko\'krak salatasi',
        'calories': 350,
        'protein': 35.0,
        'carbs': 10.0,
        'fat': 8.0,
        'meal_type': 'lunch',
        'prep_time_minutes': 20,
        'ingredients': [{'name': 'tovuq', 'amount': '200g'}, {'name': 'sabzi', 'amount': '50g'}],
        'is_recipe_of_the_day': False,
    },
    {
        'title': 'Oqshom sho\'rvasi',
        'calories': 280,
        'protein': 20.0,
        'carbs': 25.0,
        'fat': 6.0,
        'meal_type': 'dinner',
        'prep_time_minutes': 30,
        'ingredients': [{'name': 'go\'sht', 'amount': '150g'}, {'name': 'sabzavot', 'amount': '100g'}],
        'is_recipe_of_the_day': False,
    },
]
recipes = []
for rd in recipes_data:
    obj, created = Recipe.objects.get_or_create(title=rd['title'], defaults=rd)
    recipes.append(obj)
print(f"  ✓ Recipe: {len(recipes)} ta (1 recipe_of_the_day)")

# ==================================================
# 9. MEAL PLAN PREFERENCE, GENERATED MEAL PLAN, MEAL LOG
# ==================================================
print("\n[9/15] Nutrition ma'lumotlari yaratilmoqda...")
for u in [user1, user2]:
    MealPlanPreference.objects.get_or_create(
        user=u,
        defaults={
            'dietary_preferences': ['vegetarian'],
            'allergies': ['nuts'],
            'meal_types': ['breakfast', 'lunch', 'dinner'],
            'caloric_goal': 2000,
            'cooking_time_preference': 'quick',
            'number_of_servings': 2,
        }
    )
print("  ✓ MealPlanPreference: 2 ta")

gmp_count = 0
for u in [user1, user2]:
    gmp, created = GeneratedMealPlan.objects.get_or_create(
        user=u,
        date=date.today(),
        defaults={}
    )
    if created:
        gmp.recipes.set(recipes[:2])
        gmp_count += 1
print(f"  ✓ GeneratedMealPlan: {gmp_count} yangi")

ml_count = 0
for u in [user1, user2]:
    for r in recipes[:2]:
        log, created = MealLog.objects.get_or_create(
            user=u,
            recipe=r,
            logged_at=timezone.now() - timedelta(hours=3),
            defaults={
                'meal_type': r.meal_type,
                'quantity': 1.0,
            }
        )
        if created:
            ml_count += 1
print(f"  ✓ MealLog: {ml_count} yangi")

fav_r_count = 0
for u in [user1, user2]:
    obj, created = FavoriteRecipe.objects.get_or_create(user=u, recipe=recipes[0])
    if created:
        fav_r_count += 1
print(f"  ✓ FavoriteRecipe: {fav_r_count} yangi")

# ==================================================
# 10. PROGRESS ENTRIES & ACTIVITY LOGS
# ==================================================
print("\n[10/15] Progress ma'lumotlari yaratilmoqda...")
pe_count = 0
al_count = 0
for u in [user1, user2]:
    for i in range(3):
        d = date.today() - timedelta(days=i * 7)
        pe, created = ProgressEntry.objects.get_or_create(
            user=u, date=d,
            defaults={
                'weight_kg': 75.0 - i * 0.5,
                'body_fat_percentage': 18.0 - i * 0.3,
                'chest_cm': 95.0,
                'waist_cm': 80.0,
                'notes': f'{i+1}-hafta o\'lchov',
            }
        )
        if created:
            pe_count += 1
        al, created = ActivityLog.objects.get_or_create(
            user=u, date=d,
            defaults={
                'steps': 8000 + i * 500,
                'distance_km': 6.0 + i * 0.3,
                'calories_burned': 400 + i * 20,
                'active_minutes': 45 + i * 5,
                'source': 'manual',
            }
        )
        if created:
            al_count += 1
print(f"  ✓ ProgressEntry: {pe_count} yangi, ActivityLog: {al_count} yangi")

# ==================================================
# 11. COMMUNITY - FORUM
# ==================================================
print("\n[11/15] Community ma'lumotlari yaratilmoqda...")
forum_cats_data = [
    {'name': 'Umumiy', 'slug': 'general', 'order': 1},
    {'name': 'Mashqlar', 'slug': 'exercises', 'order': 2},
    {'name': 'Ovqatlanish', 'slug': 'nutrition-forum', 'order': 3},
]
forum_cats = []
for fcd in forum_cats_data:
    obj, created = ForumCategory.objects.get_or_create(slug=fcd['slug'], defaults=fcd)
    forum_cats.append(obj)
print(f"  ✓ ForumCategory: {len(forum_cats)} ta")

posts = []
posts_data = [
    {'title': 'Birinchi mashqim haqida', 'content': 'Bugun birinchi mashqimni bajardim, juda zo\'r edi!', 'user': user1, 'category': forum_cats[0]},
    {'title': 'Push-up texnikasi', 'content': 'Push-up to\'g\'ri qilish uchun qanday maslahat bor?', 'user': user2, 'category': forum_cats[1]},
    {'title': 'Protein qabuli', 'content': 'Kuniga necha gramm protein iste\'mol qilish kerak?', 'user': user1, 'category': forum_cats[2]},
]
post_count = 0
for pd in posts_data:
    obj, created = ForumPost.objects.get_or_create(
        title=pd['title'],
        defaults={'content': pd['content'], 'user': pd['user'], 'category': pd['category']}
    )
    posts.append(obj)
    if created:
        post_count += 1
print(f"  ✓ ForumPost: {post_count} yangi")

comment_count = 0
for post in posts[:2]:
    c, created = ForumComment.objects.get_or_create(
        post=post, user=user2,
        defaults={'content': 'Juda yaxshi post, rahmat!'}
    )
    if created:
        comment_count += 1
    c2, created2 = ForumComment.objects.get_or_create(
        post=post, user=user1,
        defaults={'content': 'Men ham shunday fikrdaman.'}
    )
    if created2:
        comment_count += 1
print(f"  ✓ ForumComment: {comment_count} yangi")

like_count = 0
for post in posts:
    for u in [user1, user2]:
        obj, created = PostLike.objects.get_or_create(user=u, post=post)
        if created:
            like_count += 1
print(f"  ✓ PostLike: {like_count} yangi")

# ==================================================
# 12. CHALLENGES
# ==================================================
print("\n[12/15] Challenge ma'lumotlari yaratilmoqda...")
challenges_data = [
    {
        'title': '30 kunlik Squat Challenge',
        'description': 'Har kuni squat bajaring!',
        'difficulty_level': 'beginner',
        'is_weekly': False,
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=30),
        'is_active': True,
    },
    {
        'title': 'Haftalik Cardio Challenge',
        'description': 'Bu hafta maksimal cardio!',
        'difficulty_level': 'intermediate',
        'is_weekly': True,
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=7),
        'is_active': True,
    },
    {
        'title': 'Core Strength Challenge',
        'description': 'Qorin mushaklarini kuchlashtiring',
        'difficulty_level': 'advanced',
        'is_weekly': False,
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=14),
        'is_active': True,
    },
]
challenges = []
ch_count = 0
for cd in challenges_data:
    obj, created = Challenge.objects.get_or_create(title=cd['title'], defaults=cd)
    challenges.append(obj)
    if created:
        ch_count += 1

        # ChallengeRound
        round1 = ChallengeRound.objects.create(
            challenge=obj, title='1-Bosqich', order=1
        )
        round2 = ChallengeRound.objects.create(
            challenge=obj, title='2-Bosqich', order=2
        )
        # ChallengeExercise
        ChallengeExercise.objects.create(
            round=round1, exercise=exercises[0], sets=3, reps=10, order=1
        )
        ChallengeExercise.objects.create(
            round=round2, exercise=exercises[1], sets=3, reps=15, order=1
        )
print(f"  ✓ Challenge: {ch_count} yangi (Round va Exercise bilan)")

uc_count = 0
for u in [user1, user2]:
    obj, created = UserChallenge.objects.get_or_create(
        user=u, challenge=challenges[0],
        defaults={
            'status': 'in_progress',
            'start_date': timezone.now(),
        }
    )
    if created:
        uc_count += 1
print(f"  ✓ UserChallenge: {uc_count} yangi")

# ==================================================
# 13. CONTENT - ARTICLES
# ==================================================
print("\n[13/15] Article ma'lumotlari yaratilmoqda...")
articles_data = [
    {
        'title': '10 ta Eng Yaxshi Protein Manbalar',
        'content': 'Protein ovqatlanishda juda muhim rol o\'ynaydi. Eng yaxshi manbalar: tuxum, tovuq, baliq...',
        'author': 'Dr. Salim Yusupov',
        'category': 'nutrition',
        'is_featured': True,
        'published_at': timezone.now() - timedelta(days=2),
    },
    {
        'title': 'Beginner uchun Squat Texnikasi',
        'content': 'Squat - eng asosiy mashqlardan biri. To\'g\'ri texnika juda muhim...',
        'author': 'Trainer Aziz',
        'category': 'workout',
        'is_featured': False,
        'published_at': timezone.now() - timedelta(days=5),
    },
    {
        'title': 'Motivatsiya: Maqsadga Etish Sirlari',
        'content': 'Muvaffaqiyatga etish uchun muntazamlik va intizom asosiy omillar...',
        'author': 'Kamola Tursunova',
        'category': 'motivation',
        'is_featured': True,
        'published_at': timezone.now() - timedelta(days=1),
    },
]
articles = []
art_count = 0
for ad in articles_data:
    obj, created = Article.objects.get_or_create(title=ad['title'], defaults=ad)
    articles.append(obj)
    if created:
        art_count += 1
print(f"  ✓ Article: {art_count} yangi")

fav_a_count = 0
for u in [user1, user2]:
    obj, created = FavoriteArticle.objects.get_or_create(user=u, article=articles[0])
    if created:
        fav_a_count += 1
print(f"  ✓ FavoriteArticle: {fav_a_count} yangi")

# ==================================================
# 14. NOTIFICATIONS
# ==================================================
print("\n[14/15] Notification yaratilmoqda...")
notif_count = 0
notif_data = [
    {'title': 'Xush kelibsiz!', 'body': 'FitnesApp ga xush kelibsiz. Maqsadingizni belgilang.', 'type': 'system'},
    {'title': 'Mashq vaqti!', 'body': 'Bugun mashqingizni bajarish vaqti keldi.', 'type': 'workout_reminder'},
    {'title': 'Yangi maqola', 'body': 'Nutrition bo\'limida yangi maqola e\'lon qilindi.', 'type': 'article'},
]
for u in [user1, user2]:
    for nd in notif_data:
        obj, created = Notification.objects.get_or_create(
            user=u, title=nd['title'],
            defaults={'body': nd['body'], 'type': nd['type'], 'is_read': False}
        )
        if created:
            notif_count += 1
print(f"  ✓ Notification: {notif_count} yangi")

# ==================================================
# 15. SUPPORT - FAQ & MESSAGES
# ==================================================
print("\n[15/15] Support ma'lumotlari yaratilmoqda...")
faq_data = [
    {'question': 'Parolimni qanday o\'zgartirsam bo\'ladi?', 'answer': 'Profil > Sozlamalar > Parolni o\'zgartirish', 'category': 'general', 'order': 1},
    {'question': 'Premium obuna qanday ishlaydi?', 'answer': 'Premium obuna bilan barcha mashq va ovqatlanish rejalari ochiladi.', 'category': 'workouts', 'order': 2},
    {'question': 'Kaloriya hisobi qanday amalga oshiriladi?', 'answer': 'Har bir mashq uchun kaloriya sarfi hisoblanadi.', 'category': 'nutrition', 'order': 3},
]
faq_count = 0
for fd in faq_data:
    obj, created = FAQ.objects.get_or_create(question=fd['question'], defaults=fd)
    if created:
        faq_count += 1
print(f"  ✓ FAQ: {faq_count} yangi")

sm_count = 0
for u in [user1, user2]:
    obj, created = SupportMessage.objects.get_or_create(
        user=u,
        message='Salom, Premium obuna haqida ko\'proq ma\'lumot bera olasizmi?',
        defaults={'is_from_user': True, 'is_read': False}
    )
    if created:
        sm_count += 1
print(f"  ✓ SupportMessage: {sm_count} yangi")

# ==================================================
# YAKUNIY HISOBOT
# ==================================================
print("\n" + "=" * 60)
print("  SEED YAKUNLANDI - Modellar soni:")
print("=" * 60)
print(f"  User                 : {User.objects.count()}")
print(f"  UserSettings         : {UserSettings.objects.count()}")
print(f"  UserGoal             : {UserGoal.objects.count()}")
print(f"  WorkoutCategory      : {WorkoutCategory.objects.count()}")
print(f"  Exercise             : {Exercise.objects.count()}")
print(f"  Workout              : {Workout.objects.count()}")
print(f"  WorkoutExercise      : {WorkoutExercise.objects.count()}")
print(f"  CustomRoutine        : {CustomRoutine.objects.count()}")
print(f"  CustomRoutineExercise: {CustomRoutineExercise.objects.count()}")
print(f"  UserWorkoutLog       : {UserWorkoutLog.objects.count()}")
print(f"  ExerciseLog          : {ExerciseLog.objects.count()}")
print(f"  FavoriteWorkout      : {FavoriteWorkout.objects.count()}")
print(f"  Recipe               : {Recipe.objects.count()}")
print(f"  MealPlanPreference   : {MealPlanPreference.objects.count()}")
print(f"  GeneratedMealPlan    : {GeneratedMealPlan.objects.count()}")
print(f"  MealLog              : {MealLog.objects.count()}")
print(f"  FavoriteRecipe       : {FavoriteRecipe.objects.count()}")
print(f"  ProgressEntry        : {ProgressEntry.objects.count()}")
print(f"  ActivityLog          : {ActivityLog.objects.count()}")
print(f"  ForumCategory        : {ForumCategory.objects.count()}")
print(f"  ForumPost            : {ForumPost.objects.count()}")
print(f"  ForumComment         : {ForumComment.objects.count()}")
print(f"  PostLike             : {PostLike.objects.count()}")
print(f"  Challenge            : {Challenge.objects.count()}")
print(f"  ChallengeRound       : {ChallengeRound.objects.count()}")
print(f"  ChallengeExercise    : {ChallengeExercise.objects.count()}")
print(f"  UserChallenge        : {UserChallenge.objects.count()}")
print(f"  Article              : {Article.objects.count()}")
print(f"  FavoriteArticle      : {FavoriteArticle.objects.count()}")
print(f"  Notification         : {Notification.objects.count()}")
print(f"  FAQ                  : {FAQ.objects.count()}")
print(f"  SupportMessage       : {SupportMessage.objects.count()}")
print("=" * 60)
print("  Seed muvaffaqiyatli tugadi!")
print("=" * 60)
