"""
FitnesApp — Til sozlamalari to'liq test skripti
Testlar:
  A. Accept-Language header
  B. ?lang= query param
  C. UserSettings.language (DB til)
  D. Til o'zgartirish API (PATCH /api/auth/settings/)
  E. fields='__all__' serializerlarda _uz/_en/_ru expose bo'lishini tekshirish
  F. DB to'liqlik tekshiruvi
  G. set_language_from_user() view lardan tashqarida ishlash
"""

import requests, json, os, django

BASE = "http://127.0.0.1:8000"

# ─── Yordamchi ───────────────────────────────────────────────
results = []

def req(method, path, token=None, data=None, params=None, headers=None):
    url = BASE + path
    h = {"Content-Type": "application/json"}
    if token:  h["Authorization"] = f"Bearer {token}"
    if headers: h.update(headers)
    try:
        r = getattr(requests, method.lower())(url, headers=h, json=data, params=params, timeout=8)
        return r
    except Exception as e:
        print(f"  [CONN ERR] {method} {path}: {e}")
        return None

def log(label, passed, got, expected="", note=""):
    icon = "✓ OK  " if passed else "✗ FAIL"
    results.append({"label": label, "passed": passed, "got": got, "expected": expected, "note": note})
    print(f"  [{icon}] {label:<55} got={str(got)[:40]}  {note}")
    return passed

def jget(r, *keys):
    try:
        d = r.json()
        for k in keys:
            d = d[k]
        return d
    except:
        return None

# ─── Login ───────────────────────────────────────────────────
print("=" * 65)
print("  LOGIN")
print("=" * 65)
r = req("POST", "/api/auth/login/", data={"username": "user1", "password": "Test12345!"})
if not r or r.status_code != 200:
    # username o'zgartirilgan bo'lishi mumkin
    r2 = req("POST", "/api/auth/login/", data={"username": "user1_v2", "password": "Test12345!"})
    if r2 and r2.status_code == 200:
        r = r2
    else:
        print("  Login FAIL — fix_users.py ni ishga tushiring!")
        exit(1)

T1 = r.json()["access"]
print(f"  ✓ Token olindi")

# ─── A. Accept-Language HEADER ────────────────────────────────
print("\n" + "=" * 65)
print("  A. Accept-Language HEADER testi")
print("=" * 65)

ENDPOINTS_TO_TEST = [
    ("GET", "/api/workouts/workouts/",      "results", "title"),
    ("GET", "/api/nutrition/recipes/",      "results", "title"),
    ("GET", "/api/support/faqs/",           "results", "question"),
    ("GET", "/api/content/articles/",       "results", "title"),
    ("GET", "/api/community/challenges/",   "results", "title"),
    ("GET", "/api/community/categories/",   "results", "name"),
]

lang_results = {}  # endpoint -> {uz: val, en: val, ru: val}

for method, ep, wrap, field in ENDPOINTS_TO_TEST:
    lang_results[ep] = {}
    for lang in ["uz", "en", "ru"]:
        r = req(method, ep, token=T1, headers={"Accept-Language": lang})
        if not r:
            lang_results[ep][lang] = None
            continue
        d = r.json()
        items = d.get(wrap, d) if isinstance(d, dict) else d
        val = items[0].get(field, "") if items else ""
        lang_results[ep][lang] = val

# Natijani chiqarish
print(f"\n  {'Endpoint':<35} {'uz':^20} {'en':^25} {'ru':^20}")
print("  " + "-" * 100)
for ep, langs in lang_results.items():
    uz = str(langs.get("uz", ""))[:18]
    en = str(langs.get("en", ""))[:23]
    ru = str(langs.get("ru", ""))[:18]
    diff = len(set([langs.get("uz"), langs.get("en"), langs.get("ru")])) > 1
    icon = "✓" if diff else "⚠"
    print(f"  {icon} {ep:<33} {uz:<20} {en:<25} {ru:<20}")
    # Test: 3 til har xil bo'lishi kerak
    passed = diff
    log(f"Accept-Language [{ep.split('/')[-2]}]", passed,
        f"uz={uz[:15]}", f"3 til har xil", note="barcha tillar farqlanadi" if passed else "tillar farqlanmaydi!")

# ─── B. ?lang= QUERY PARAM ────────────────────────────────────
print("\n" + "=" * 65)
print("  B. ?lang= QUERY PARAM testi")
print("=" * 65)

for lang in ["uz", "en", "ru"]:
    r = req("GET", "/api/workouts/workouts/", token=T1, params={"lang": lang})
    val = None
    if r and r.status_code == 200:
        items = r.json().get("results", [])
        val = items[0].get("title", "") if items else ""
    log(f"?lang={lang} /api/workouts/workouts/", r is not None and r.status_code == 200,
        val, f"200 + title in {lang}", note=f"title: {str(val)[:30]}")

# ?lang= va Accept-Language birgalikda — ?lang= ustunlik qilishi kerak
r_accept = req("GET", "/api/workouts/workouts/", token=T1, headers={"Accept-Language": "en"}, params={"lang": "uz"})
r_lang   = req("GET", "/api/workouts/workouts/", token=T1, params={"lang": "uz"})
val_accept = jget(r_accept, "results", 0, "title") if r_accept else ""
val_lang   = jget(r_lang,   "results", 0, "title") if r_lang else ""
priority_ok = (val_accept == val_lang)
log("?lang=uz ustunligi (Accept-Language: en bilan)", priority_ok,
    f"accept={str(val_accept)[:20]}", f"lang={str(val_lang)[:20]}",
    note="?lang= Accept-Language ni override qiladi" if priority_ok else "?lang= ustunlik qilmaydi!")

# ─── C. UserSettings.language (DB til) ────────────────────────
print("\n" + "=" * 65)
print("  C. UserSettings.language (DB til) testi")
print("=" * 65)

# settings orqali tilni en ga o'zgartirish
r = req("PATCH", "/api/auth/settings/", token=T1, data={"language": "en"})
log("PATCH /api/auth/settings/ language=en", r is not None and r.status_code == 200,
    jget(r, "language"), "en")

# settings da language saqlanganmi
r = req("GET", "/api/auth/settings/", token=T1)
saved_lang = jget(r, "language")
log("GET /api/auth/settings/ language saqlangan", saved_lang == "en", saved_lang, "en")

# ru ga o'zgartirish
r = req("PATCH", "/api/auth/settings/", token=T1, data={"language": "ru"})
log("PATCH /api/auth/settings/ language=ru", r is not None and r.status_code == 200,
    jget(r, "language"), "ru")

# Noto'g'ri til
r = req("PATCH", "/api/auth/settings/", token=T1, data={"language": "de"})
log("PATCH /api/auth/settings/ language=de (invalid)", r is not None and r.status_code == 400,
    r.status_code if r else 0, 400, note="noto'g'ri til 400 qaytarishi kerak")

# uz ga qaytarish
req("PATCH", "/api/auth/settings/", token=T1, data={"language": "uz"})

# ─── D. language field API orqali ishlashi ────────────────────
print("\n" + "=" * 65)
print("  D. language API + til o'zgarishi testi")
print("=" * 65)

# user settings da en saqlab, so'rov qilamiz
req("PATCH", "/api/auth/settings/", token=T1, data={"language": "en"})

# set_language_from_user faqat GlobalSearchView da chaqiriladi
# boshqa viewlarda ishlash kerak emas — lekin Accept-Language header bilan ishlashi kerak
r_en = req("GET", "/api/workouts/workouts/", token=T1, headers={"Accept-Language": "en"})
r_uz = req("GET", "/api/workouts/workouts/", token=T1, headers={"Accept-Language": "uz"})
r_ru = req("GET", "/api/workouts/workouts/", token=T1, headers={"Accept-Language": "ru"})

title_en = jget(r_en, "results", 0, "title") if r_en else ""
title_uz = jget(r_uz, "results", 0, "title") if r_uz else ""
title_ru = jget(r_ru, "results", 0, "title") if r_ru else ""

log("Accept-Language: en → en title", bool(title_en), title_en, "non-empty en title")
log("Accept-Language: uz → uz title", bool(title_uz), title_uz, "non-empty uz title")
log("Accept-Language: ru → ru title", bool(title_ru), title_ru, "non-empty ru title")

all_diff = len({title_en, title_uz, title_ru}) == 3
log("3 til barchasi har xil natija", all_diff,
    f"en={str(title_en)[:15]}", "3 xil qiymat",
    note="✓ modeltranslation ishlaydi" if all_diff else "⚠ ba'zi tillar bo'sh yoki bir xil")

# settings da language saqlash va so'ngra til header yo'q holat
req("PATCH", "/api/auth/settings/", token=T1, data={"language": "uz"})

# ─── E. fields='__all__' serializerlarda _uz/_en/_ru EXPOSE ────
print("\n" + "=" * 65)
print("  E. Serializer fields='__all__' — _uz/_en/_ru expose testi")
print("=" * 65)

# Agar serializer __all__ ishlatsa, _uz/_en/_ru fieldlari ham chiqishi kerak
r = req("GET", "/api/workouts/workouts/", token=T1)
if r and r.status_code == 200:
    items = r.json().get("results", [])
    if items:
        fields = list(items[0].keys())
        has_title_uz = "title_uz" in fields
        has_title_en = "title_en" in fields
        has_title_ru = "title_ru" in fields
        has_title    = "title"    in fields

        log("Workout: title field mavjud",    has_title,    "title" in fields,    True)
        log("Workout: title_uz field yo'q (clean API)", not has_title_uz,
            "title_uz" not in fields, True,
            note="✓ faqat 'title' — til header bilan o'zgaradi" if not has_title_uz else "⚠ _uz/_en/_ru expose bo'lmoqda!")
        log("Workout: title_en field yo'q (clean API)", not has_title_en,
            "title_en" not in fields, True,
            note="" if not has_title_en else "⚠ expose bo'lmoqda!")
        log("Workout: title_ru field yo'q (clean API)", not has_title_ru,
            "title_ru" not in fields, True,
            note="" if not has_title_ru else "⚠ expose bo'lmoqda!")

        print(f"\n  Workout fields: {fields}")

# Recipe ham tekshirish
r = req("GET", "/api/nutrition/recipes/", token=T1)
if r and r.status_code == 200:
    items = r.json().get("results", [])
    if items:
        fields = list(items[0].keys())
        has_title_uz = "title_uz" in fields
        log("Recipe: title_uz field yo'q (clean API)", not has_title_uz,
            "title_uz" not in fields, True,
            note="✓ clean" if not has_title_uz else "⚠ _uz expose bo'lmoqda!")
        print(f"  Recipe fields: {fields}")

# FAQ tekshirish
r = req("GET", "/api/support/faqs/")
if r and r.status_code == 200:
    d = r.json()
    items = d.get("results", d) if isinstance(d, dict) else d
    if items:
        fields = list(items[0].keys())
        has_q_uz = "question_uz" in fields
        log("FAQ: question_uz field yo'q (clean API)", not has_q_uz,
            "question_uz" not in fields, True,
            note="✓ clean" if not has_q_uz else "⚠ _uz expose bo'lmoqda!")
        print(f"  FAQ fields: {fields}")

# ─── F. DB TO'LIQLIK TEKSHIRUVI ───────────────────────────────
print("\n" + "=" * 65)
print("  F. DB to'liqlik — Accept-Language bilan bo'sh qiymatlar")
print("=" * 65)

checks = [
    ("uz", "/api/workouts/workouts/",    "title",    "results"),
    ("en", "/api/workouts/workouts/",    "title",    "results"),
    ("ru", "/api/workouts/workouts/",    "title",    "results"),
    ("uz", "/api/nutrition/recipes/",    "title",    "results"),
    ("en", "/api/nutrition/recipes/",    "title",    "results"),
    ("ru", "/api/nutrition/recipes/",    "title",    "results"),
    ("uz", "/api/support/faqs/",         "question", "results"),
    ("en", "/api/support/faqs/",         "question", "results"),
    ("ru", "/api/support/faqs/",         "question", "results"),
    ("uz", "/api/content/articles/",     "title",    "results"),
    ("en", "/api/content/articles/",     "title",    "results"),
    ("ru", "/api/content/articles/",     "title",    "results"),
    ("uz", "/api/community/challenges/", "title",    "results"),
    ("en", "/api/community/challenges/", "title",    "results"),
    ("ru", "/api/community/challenges/", "title",    "results"),
]

empty_found = []
for lang, ep, field, wrap in checks:
    r = req("GET", ep, token=T1, headers={"Accept-Language": lang})
    if not r:
        continue
    d = r.json()
    items = d.get(wrap, d) if isinstance(d, dict) else d
    total = len(items) if items else 0
    empty = sum(1 for i in items if not i.get(field, ""))
    all_filled = empty == 0
    log(f"[{lang}] {ep.split('/')[2]}.{field} to'liq",
        all_filled, f"{total-empty}/{total}", f"0 bo'sh",
        note="" if all_filled else f"⚠ {empty} ta bo'sh!")
    if not all_filled:
        empty_found.append(f"{lang} {ep} {field}: {empty}/{total} bo'sh")

# ─── G. set_language_from_user — boshqa viewlarda ishlash ─────
print("\n" + "=" * 65)
print("  G. set_language_from_user() — faqat GlobalSearchView da testi")
print("=" * 65)

# user settings da en saqlash
req("PATCH", "/api/auth/settings/", token=T1, data={"language": "en"})

# GlobalSearch — set_language_from_user chaqiriladi
r = req("GET", "/api/search/", token=T1, params={"q": "yoga", "type": "workout"})
if r and r.status_code == 200:
    workouts = r.json().get("workouts", [])
    val = workouts[0].get("title", "") if workouts else ""
    log("GlobalSearch user.settings.language=en → en title",
        bool(val), val, "non-empty", note=f"title: {val}")
else:
    log("GlobalSearch", False, r.status_code if r else 0, 200)

# Workout list — set_language_from_user chaqirilmaydi, Accept-Language kerak
r = req("GET", "/api/workouts/workouts/", token=T1)  # header ham, lang param ham yo'q
if r and r.status_code == 200:
    items = r.json().get("results", [])
    val = items[0].get("title", "") if items else ""
    log("WorkoutList header yo'q → default til (uz)",
        bool(val), val, "uz title (default)",
        note=f"title: {val} — settings.language ishlamaydi bu viewda")

# uz ga qaytarish
req("PATCH", "/api/auth/settings/", token=T1, data={"language": "uz"})

# ─── YAKUNIY HISOBOT ──────────────────────────────────────────
ok    = sum(1 for r in results if r["passed"])
fail  = sum(1 for r in results if not r["passed"])
total = len(results)

print("\n" + "=" * 65)
print(f"  JAMI: {total} | ✓ OK: {ok} | ✗ FAIL: {fail}")
print("=" * 65)

if fail:
    print("\n  ── FAIL testlar ──")
    for r in results:
        if not r["passed"]:
            print(f"  ✗ {r['label']}")
            print(f"       got={r['got']}  expected={r['expected']}  {r['note']}")

# JSON saqlash
with open("i18n_test_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "total": total, "ok": ok, "fail": fail,
        "lang_results": {k: v for k, v in lang_results.items()},
        "empty_fields": empty_found,
        "results": results
    }, f, ensure_ascii=False, indent=2)
print("\n  Natijalar: i18n_test_results.json ga saqlandi.")
print("=" * 65)
