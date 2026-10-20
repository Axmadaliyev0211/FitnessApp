"""
Noto'g'ri test ma'lumotlari bo'lgan Challengelarni to'g'rilash.
'vfghjn', 'Test Challenge', 'fdghjgfd' kabi ma'lumotlarni tozalash.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from community.models import Challenge, ForumPost, ForumCategory

print("=== Challenge lar holati ===")
for ch in Challenge.objects.all():
    print(f"  id={ch.id} | uz={ch.title_uz!r} | en={ch.title_en!r} | ru={ch.title_ru!r}")

# 'vfghjn' va 'Test Challenge' larni tozalash/to'g'rilash
fixes = {
    'vfghjn': {
        'title_uz': 'Umumiy Challenge',
        'title_en': 'General Challenge',
        'title_ru': 'Общий челлендж',
        'description_uz': 'Umumiy fitness challenge.',
        'description_en': 'General fitness challenge.',
        'description_ru': 'Общий фитнес-челлендж.',
    },
    'Test Challenge': {
        'title_uz': 'Sinovchi Challenge',
        'title_en': 'Trial Challenge',
        'title_ru': 'Пробный челлендж',
        'description_uz': 'Sinovchi challenge.',
        'description_en': 'Trial challenge.',
        'description_ru': 'Пробный челлендж.',
    },
}

updated = 0
for ch in Challenge.objects.all():
    key = ch.title_uz or ch.title_en or ch.title
    if key in fixes:
        for field, val in fixes[key].items():
            setattr(ch, field, val)
        ch.save()
        updated += 1
        print(f"  ✓ Yangilandi: {key!r} → {fixes[key]['title_uz']!r}")

print(f"\n  Jami yangilandi: {updated} ta Challenge")

# ForumPost larda ham noto'g'ri ma'lumotlar bo'lishi mumkin
print("\n=== ForumPost lar holati ===")
for fp in ForumPost.objects.all():
    title = fp.title_uz or fp.title_en or fp.title
    print(f"  id={fp.id} | uz={fp.title_uz!r} | en={fp.title_en!r}")
    if title in ('fdghjgfd', 'vfghjn', 'test', 'Test'):
        fp.title_uz = 'Test Forum Posti'
        fp.title_en = 'Test Forum Post'
        fp.title_ru = 'Тестовый пост'
        fp.content_uz = fp.content_uz or 'Ushbu post test uchun.'
        fp.content_en = fp.content_en or 'This post is for testing.'
        fp.content_ru = fp.content_ru or 'Этот пост для тестирования.'
        fp.save()
        print(f"  ✓ ForumPost tuzatildi: {title!r}")

print("\n=== Yakuniy holat ===")
for ch in Challenge.objects.all():
    print(f"  uz={ch.title_uz!r} | en={ch.title_en!r} | ru={ch.title_ru!r}")
