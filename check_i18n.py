import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.utils import translation
from django.conf import settings
from workouts.models import Workout
from nutrition.models import Recipe
from support.models import FAQ
from community.models import Challenge
from users.models import UserGoal

# ─── 1. Til sozlamalari ───────────────────────────────────────────
print("=" * 55)
print("  i18n / modeltranslation SOZLAMALARI")
print("=" * 55)
print(f"  USE_I18N                         : {settings.USE_I18N}")
print(f"  LANGUAGE_CODE                    : {settings.LANGUAGE_CODE}")
print(f"  LANGUAGES                        : {[l[0] for l in settings.LANGUAGES]}")
print(f"  MODELTRANSLATION_LANGUAGES       : {settings.MODELTRANSLATION_LANGUAGES}")
print(f"  MODELTRANSLATION_DEFAULT_LANGUAGE: {settings.MODELTRANSLATION_DEFAULT_LANGUAGE}")

locale_mw = any("LocaleMiddleware" in m for m in settings.MIDDLEWARE)
print(f"  LocaleMiddleware mavjud          : {locale_mw}")

locale_dir = os.path.join(settings.BASE_DIR, 'locale')
print(f"  locale/ papkasi mavjud           : {os.path.isdir(locale_dir)}")

# ─── 2. Til override bilan field qiymatlari ───────────────────────
print()
print("=" * 55)
print("  MODELLAR: til override bilan qiymatlar")
print("=" * 55)

w = Workout.objects.first()
if w:
    print(f"\n  Workout: '{w.title_en or w.title}'")
    for lang in ['uz', 'en', 'ru']:
        with translation.override(lang):
            print(f"    [{lang}] title = {w.title!r}")

r = Recipe.objects.first()
if r:
    print(f"\n  Recipe: '{r.title_en or r.title}'")
    for lang in ['uz', 'en', 'ru']:
        with translation.override(lang):
            print(f"    [{lang}] title = {r.title!r}")

faq = FAQ.objects.first()
if faq:
    print(f"\n  FAQ: '{faq.question_en or faq.question}'")
    for lang in ['uz', 'en', 'ru']:
        with translation.override(lang):
            print(f"    [{lang}] question = {faq.question!r}")

ch = Challenge.objects.first()
if ch:
    print(f"\n  Challenge: '{ch.title_uz or ch.title_en or ch.title}'")
    for lang in ['uz', 'en', 'ru']:
        with translation.override(lang):
            print(f"    [{lang}] title = {ch.title!r}")

# ─── 3. DB dagi tarjima fieldlari to'ldirilganmi? ─────────────────
print()
print("=" * 55)
print("  DB: tarjima fieldlari to'ldirish holati")
print("=" * 55)

checks = [
    ("Workout", "title_uz", Workout),
    ("Workout", "title_en", Workout),
    ("Workout", "title_ru", Workout),
    ("Recipe", "title_uz", Recipe),
    ("Recipe", "title_en", Recipe),
    ("Recipe", "title_ru", Recipe),
    ("FAQ", "question_uz", FAQ),
    ("FAQ", "question_en", FAQ),
    ("FAQ", "question_ru", FAQ),
    ("Challenge", "title_uz", Challenge),
    ("Challenge", "title_en", Challenge),
    ("Challenge", "title_ru", Challenge),
]

for model_name, field, Model in checks:
    total = Model.objects.count()
    filled = Model.objects.exclude(**{f"{field}__isnull": True}).exclude(**{f"{field}__exact": ""}).count()
    pct = round(filled / total * 100) if total else 0
    status = "✅" if pct > 80 else ("⚠️ " if pct > 0 else "❌")
    print(f"  {status} {model_name}.{field:<20} : {filled}/{total} to'ldirilgan ({pct}%)")

# ─── 4. modeltranslation ro'yxatdan o'tgan modellar ──────────────
print()
print("=" * 55)
print("  MODELTRANSLATION: ro'yxatdan o'tgan modellar")
print("=" * 55)

from modeltranslation.translator import translator
registered = translator.get_registered_models()
for model in registered:
    opts = translator.get_options_for_model(model)
    app = model._meta.app_label
    fields = list(opts.fields) if isinstance(opts.fields, (list, tuple)) else list(opts.fields.keys())
    print(f"  [{app}] {model.__name__:<25} → fields: {fields}")
