"""
FitnesApp — Yangilangan To'liq API Test Skripti
Testlar: Funksional, Xavfsizlik, Validation, Filter, Ruxsatlar, Flow, Performance
Sana: 2026-09-21 (Qayta test)
"""

import requests
import json
import time
import sys
from datetime import date, datetime, timedelta

BASE = "http://127.0.0.1:8000"
H_JSON = {"Content-Type": "application/json"}

# ── Natija yig'ish ────────────────────────────────────────
results = []
ok_count = 0
fail_count = 0

def log(method, endpoint, expected, got, note="", section="FUNCTIONAL"):
    global ok_count, fail_count
    if isinstance(expected, (list, tuple)):
        passed = got in expected
    else:
        passed = (got == expected)
    flag = "✓ OK  " if passed else "✗ FAIL"
    if passed: ok_count += 1
    else:       fail_count += 1
    results.append(dict(section=section, method=method, endpoint=endpoint,
                        expected=expected, got=got, note=note, passed=passed))
    print(f"  [{flag}] {method:7} {endpoint[:55]:<55} exp={expected} got={got}  {note}")
    return passed

def req(method, path, token=None, data=None, params=None):
    url = BASE + path
    headers = dict(H_JSON)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        t0 = time.time()
        r = getattr(requests, method.lower())(
            url, headers=headers, json=data, params=params, timeout=10
        )
        return r, round(time.time()-t0, 3)
    except Exception as e:
        print(f"    [CONN ERR] {method} {path}: {e}")
        return None, 0

def jget(r, key, default=None):
    try: return r.json().get(key, default)
    except: return default

def first_id(r):
    try:
        d = r.json()
        res = d.get("results", d) if isinstance(d, dict) else d
        if isinstance(res, list) and res:
            return res[0].get("id")
    except: pass
    return None

# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  TOKENLAR OLINMOQDA")
print("="*70)

r, _ = req("POST", "/api/auth/login/", data={"username":"user1","password":"Test12345!"})
assert r and r.status_code == 200, f"user1 login FAIL: {r.status_code if r else 'no response'}"
T1 = r.json()["access"]; R1 = r.json()["refresh"]
print("  ✓ user1 token olindi")

r, _ = req("POST", "/api/auth/login/", data={"username":"user2","password":"Test12345!"})
assert r and r.status_code == 200
T2 = r.json()["access"]
print("  ✓ user2 token olindi")

r, _ = req("POST", "/api/auth/login/", data={"username":"trainer","password":"Test12345!"})
assert r and r.status_code == 200
TT = r.json()["access"]
print("  ✓ trainer token olindi")

# ═══════════════════════════════════════════════════════════
# BOSQICH 1: FUNKSIONAL TESTLAR
# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  FUNKSIONAL API TESTLAR")
print("="*70)

# ── AUTH ────────────────────────────────────────────────
print("\n  ── AUTH ──")
# Register (password + password2 kerak)
r, _ = req("POST", "/api/auth/register/", data={
    "email":"newtest2026@test.com","nickname":"newtest2026",
    "full_name":"New Test","password":"NewPass123!","password2":"NewPass123!"
})
log("POST","/api/auth/register/",(200,201),r.status_code if r else 0)

r, _ = req("POST", "/api/auth/login/", data={"username":"user1","password":"Test12345!"})
log("POST","/api/auth/login/",200,r.status_code if r else 0)

r, _ = req("POST", "/api/auth/token/refresh/", data={"refresh":R1})
log("POST","/api/auth/token/refresh/",200,r.status_code if r else 0)
NEW_T1 = r.json().get("access") if r and r.status_code==200 else T1

r, _ = req("GET",  "/api/auth/me/", token=T1)
log("GET", "/api/auth/me/",200,r.status_code if r else 0)

r, _ = req("PATCH","/api/auth/me/", token=T1, data={"nickname":"user1_v2"})
log("PATCH","/api/auth/me/",200,r.status_code if r else 0)

# Onboarding — endi bitta view (tuzatildi)
r, _ = req("POST","/api/auth/onboarding/", token=T1, data={
    "gender":"male","fitness_level":"intermediate",
    "primary_goal":"muscle_mass_gain","height_cm":178,"weight_kg":73
})
log("POST","/api/auth/onboarding/",200,r.status_code if r else 0, note="tuzatilgan view")

r, _ = req("GET", "/api/auth/settings/", token=T1)
log("GET", "/api/auth/settings/",200,r.status_code if r else 0)

r, _ = req("PATCH","/api/auth/settings/", token=T1, data={"notifications_enabled":False})
log("PATCH","/api/auth/settings/",200,r.status_code if r else 0)

r, _ = req("GET", "/api/auth/goals/", token=T1)
log("GET", "/api/auth/goals/",200,r.status_code if r else 0)

r, _ = req("POST","/api/auth/goals/", token=T1, data={
    "goal_type":"lose_weight","title":"Yangi Maqsad",
    "target_value":"65.00","current_value":"73.00","unit":"kg",
    "start_date":str(date.today()),
    "end_date":str(date.today()+timedelta(days=60))
})
log("POST","/api/auth/goals/",(200,201),r.status_code if r else 0)
GOAL_ID = jget(r,"id") if r and r.status_code in [200,201] else None

if GOAL_ID:
    r, _ = req("GET",   f"/api/auth/goals/{GOAL_ID}/", token=T1)
    log("GET",  "/api/auth/goals/{id}/",200,r.status_code if r else 0)
    r, _ = req("PATCH", f"/api/auth/goals/{GOAL_ID}/", token=T1, data={"title":"Yangilangan"})
    log("PATCH","/api/auth/goals/{id}/",200,r.status_code if r else 0)
    r, _ = req("POST",  f"/api/auth/goals/{GOAL_ID}/complete/", token=T1)
    log("POST", "/api/auth/goals/{id}/complete/",200,r.status_code if r else 0)
    r, _ = req("DELETE",f"/api/auth/goals/{GOAL_ID}/", token=T1)
    log("DELETE","/api/auth/goals/{id}/",204,r.status_code if r else 0)

r, _ = req("POST","/api/auth/change-password/", token=T1, data={
    "current_password":"Test12345!","new_password":"Test12345!","new_password2":"Test12345!"
})
log("POST","/api/auth/change-password/",200,r.status_code if r else 0)

r, _ = req("POST","/api/auth/forgot-password/", data={"email":"user1@test.com"})
log("POST","/api/auth/forgot-password/",200,r.status_code if r else 0, note="email console da")

# ── WORKOUTS ────────────────────────────────────────────
print("\n  ── WORKOUTS ──")
r, _ = req("GET","/api/workouts/categories/", token=T1)
log("GET","/api/workouts/categories/",200,r.status_code if r else 0)

r, _ = req("GET","/api/workouts/exercises/", token=T1)
log("GET","/api/workouts/exercises/",200,r.status_code if r else 0)

r, _ = req("GET","/api/workouts/workouts/", token=T1)
log("GET","/api/workouts/workouts/",200,r.status_code if r else 0)
WID = first_id(r)

r, _ = req("GET","/api/workouts/workouts/training_of_the_day/", token=T1)
log("GET","/api/workouts/workouts/training_of_the_day/",200,r.status_code if r else 0)

r, _ = req("GET","/api/workouts/workouts/recommended/", token=T1)
log("GET","/api/workouts/workouts/recommended/",200,r.status_code if r else 0)

if WID:
    r, _ = req("GET",f"/api/workouts/workouts/{WID}/", token=T1)
    log("GET","/api/workouts/workouts/{id}/",200,r.status_code if r else 0)

# Trainer: workout CRUD
r, _ = req("POST","/api/workouts/workouts/", token=TT, data={
    "title":"Trainer New Workout","difficulty_level":"beginner",
    "duration_minutes":20,"calories_estimated":150
})
log("POST","/api/workouts/workouts/",(200,201),r.status_code if r else 0, note="trainer")
NW_ID = jget(r,"id") if r and r.status_code in [200,201] else None

if NW_ID:
    r, _ = req("PATCH",f"/api/workouts/workouts/{NW_ID}/", token=TT, data={"title":"Updated Workout"})
    log("PATCH","/api/workouts/workouts/{id}/",200,r.status_code if r else 0, note="trainer")
    r, _ = req("DELETE",f"/api/workouts/workouts/{NW_ID}/", token=TT)
    log("DELETE","/api/workouts/workouts/{id}/",204,r.status_code if r else 0, note="trainer")

r, _ = req("GET", "/api/workouts/custom-routines/", token=T1)
log("GET","/api/workouts/custom-routines/",200,r.status_code if r else 0)
r, _ = req("POST","/api/workouts/custom-routines/", token=T1, data={"title":"My Routine"})
log("POST","/api/workouts/custom-routines/",(200,201),r.status_code if r else 0)
CR_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if CR_ID:
    r, _ = req("PATCH",f"/api/workouts/custom-routines/{CR_ID}/", token=T1, data={"title":"Updated"})
    log("PATCH","/api/workouts/custom-routines/{id}/",200,r.status_code if r else 0)
    r, _ = req("DELETE",f"/api/workouts/custom-routines/{CR_ID}/", token=T1)
    log("DELETE","/api/workouts/custom-routines/{id}/",204,r.status_code if r else 0)

r, _ = req("GET", "/api/workouts/logs/", token=T1)
log("GET","/api/workouts/logs/",200,r.status_code if r else 0)
r, _ = req("POST","/api/workouts/logs/", token=T1, data={
    "workout":WID,"started_at":datetime.now().isoformat()
})
log("POST","/api/workouts/logs/",(200,201),r.status_code if r else 0)
LOG_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if LOG_ID:
    r, _ = req("POST",f"/api/workouts/logs/{LOG_ID}/complete/", token=T1, data={
        "completed_at":datetime.now().isoformat(),
        "duration_seconds":1800,"rating":5,"calories_burned":250
    })
    log("POST","/api/workouts/logs/{id}/complete/",200,r.status_code if r else 0)

r, _ = req("GET", "/api/workouts/favorites/", token=T1)
log("GET","/api/workouts/favorites/",200,r.status_code if r else 0)

# *** workout field (workout_id emas) — yangilangan serializer
r, _ = req("POST","/api/workouts/favorites/", token=T1, data={"workout":WID})
log("POST","/api/workouts/favorites/",(200,201,400),r.status_code if r else 0, note="workout field")
FW_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if FW_ID:
    r, _ = req("DELETE",f"/api/workouts/favorites/{FW_ID}/", token=T1)
    log("DELETE","/api/workouts/favorites/{id}/",204,r.status_code if r else 0)

# ── NUTRITION ───────────────────────────────────────────
print("\n  ── NUTRITION ──")
r, _ = req("GET","/api/nutrition/recipes/", token=T1)
log("GET","/api/nutrition/recipes/",200,r.status_code if r else 0)
RCP_ID = first_id(r)

r, _ = req("GET","/api/nutrition/recipes/recipe_of_the_day/", token=T1)
log("GET","/api/nutrition/recipes/recipe_of_the_day/",(200,404),r.status_code if r else 0)

r, _ = req("GET","/api/nutrition/recipes/recommended/", token=T1)
log("GET","/api/nutrition/recipes/recommended/",200,r.status_code if r else 0)

if RCP_ID:
    r, _ = req("GET",f"/api/nutrition/recipes/{RCP_ID}/", token=T1)
    log("GET","/api/nutrition/recipes/{id}/",200,r.status_code if r else 0)

r, _ = req("GET", "/api/nutrition/preferences/", token=T1)
log("GET","/api/nutrition/preferences/",200,r.status_code if r else 0)
r, _ = req("PATCH","/api/nutrition/preferences/", token=T1, data={
    "dietary_preferences":["vegan"],"allergies":[],"meal_types":["breakfast","lunch"],
    "caloric_goal":1800,"number_of_servings":1
})
log("PATCH","/api/nutrition/preferences/",200,r.status_code if r else 0, note="RetrieveUpdateAPIView")

r, _ = req("GET", "/api/nutrition/meal-plans/", token=T1)
log("GET","/api/nutrition/meal-plans/",200,r.status_code if r else 0)
r, _ = req("POST","/api/nutrition/meal-plans/", token=T1, data={"date":str(date.today())})
log("POST","/api/nutrition/meal-plans/",(200,201),r.status_code if r else 0)

r, _ = req("GET","/api/nutrition/meal-logs/", token=T1)
log("GET","/api/nutrition/meal-logs/",200,r.status_code if r else 0)

# *** recipe field (recipe_id emas) — yangilangan serializer
r, _ = req("POST","/api/nutrition/meal-logs/", token=T1, data={
    "recipe":RCP_ID,"meal_type":"breakfast",
    "quantity":"1.00","logged_at":datetime.now().isoformat()
})
log("POST","/api/nutrition/meal-logs/",(200,201),r.status_code if r else 0, note="recipe field")
ML_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if ML_ID:
    r, _ = req("PATCH",f"/api/nutrition/meal-logs/{ML_ID}/", token=T1, data={"quantity":"2.00"})
    log("PATCH","/api/nutrition/meal-logs/{id}/",200,r.status_code if r else 0)
    r, _ = req("DELETE",f"/api/nutrition/meal-logs/{ML_ID}/", token=T1)
    log("DELETE","/api/nutrition/meal-logs/{id}/",204,r.status_code if r else 0)

r, _ = req("GET","/api/nutrition/meal-logs/summary/", token=T1)
log("GET","/api/nutrition/meal-logs/summary/",(200,404),r.status_code if r else 0)

r, _ = req("GET","/api/nutrition/favorites/", token=T1)
log("GET","/api/nutrition/favorites/",200,r.status_code if r else 0)

# *** recipe field — yangilangan serializer
r, _ = req("POST","/api/nutrition/favorites/", token=T1, data={"recipe":RCP_ID})
log("POST","/api/nutrition/favorites/",(200,201,400),r.status_code if r else 0, note="recipe field")
FR_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if FR_ID:
    r, _ = req("DELETE",f"/api/nutrition/favorites/{FR_ID}/", token=T1)
    log("DELETE","/api/nutrition/favorites/{id}/",204,r.status_code if r else 0)

# ── PROGRESS ────────────────────────────────────────────
print("\n  ── PROGRESS ──")
r, _ = req("GET","/api/progress/entries/", token=T1)
log("GET","/api/progress/entries/",200,r.status_code if r else 0)
r, _ = req("POST","/api/progress/entries/", token=T1, data={
    "date":str(date.today()-timedelta(days=300)),
    "weight_kg":"72.50","notes":"qayta test"
})
log("POST","/api/progress/entries/",(200,201),r.status_code if r else 0)
PE_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if PE_ID:
    r, _ = req("GET",   f"/api/progress/entries/{PE_ID}/", token=T1)
    log("GET",  "/api/progress/entries/{id}/",200,r.status_code if r else 0)
    r, _ = req("PATCH", f"/api/progress/entries/{PE_ID}/", token=T1, data={"weight_kg":"71.00"})
    log("PATCH","/api/progress/entries/{id}/",200,r.status_code if r else 0)
    r, _ = req("DELETE",f"/api/progress/entries/{PE_ID}/", token=T1)
    log("DELETE","/api/progress/entries/{id}/",204,r.status_code if r else 0)

r, _ = req("GET","/api/progress/entries/charts/", token=T1, params={"period":"month"})
log("GET","/api/progress/entries/charts/",200,r.status_code if r else 0)

r, _ = req("GET","/api/progress/activity/", token=T1)
log("GET","/api/progress/activity/",200,r.status_code if r else 0)
r, _ = req("POST","/api/progress/activity/", token=T1, data={
    "date":str(date.today()-timedelta(days=300)),
    "steps":9000,"distance_km":"6.50","calories_burned":420,"active_minutes":50,"source":"manual"
})
log("POST","/api/progress/activity/",(200,201),r.status_code if r else 0)
AL_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if AL_ID:
    r, _ = req("PATCH", f"/api/progress/activity/{AL_ID}/", token=T1, data={"steps":10000})
    log("PATCH","/api/progress/activity/{id}/",200,r.status_code if r else 0)
    r, _ = req("DELETE",f"/api/progress/activity/{AL_ID}/", token=T1)
    log("DELETE","/api/progress/activity/{id}/",204,r.status_code if r else 0)

# ── COMMUNITY ───────────────────────────────────────────
print("\n  ── COMMUNITY ──")
r, _ = req("GET","/api/community/categories/", token=T1)
log("GET","/api/community/categories/",200,r.status_code if r else 0)

r, _ = req("GET","/api/community/posts/", token=T1)
log("GET","/api/community/posts/",200,r.status_code if r else 0)
POST_ID = first_id(r)

r, _ = req("POST","/api/community/posts/", token=T1, data={
    "title":"Qayta Test Post","content":"Bu qayta test uchun.","category":3
})
log("POST","/api/community/posts/",(200,201),r.status_code if r else 0)
NP_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if NP_ID:
    r, _ = req("GET",   f"/api/community/posts/{NP_ID}/", token=T1)
    log("GET",  "/api/community/posts/{id}/",200,r.status_code if r else 0)
    r, _ = req("PATCH", f"/api/community/posts/{NP_ID}/", token=T1, data={"content":"Yangilangan"})
    log("PATCH","/api/community/posts/{id}/",200,r.status_code if r else 0)

r, _ = req("GET","/api/community/comments/", token=T1)
log("GET","/api/community/comments/",200,r.status_code if r else 0)

use_post = NP_ID or POST_ID
if use_post:
    r, _ = req("POST","/api/community/comments/", token=T2, data={
        "post":use_post,"content":"Test izoh"
    })
    log("POST","/api/community/comments/",(200,201),r.status_code if r else 0)
    CM_ID = jget(r,"id") if r and r.status_code in [200,201] else None
    if CM_ID:
        r, _ = req("PATCH", f"/api/community/comments/{CM_ID}/", token=T2, data={"content":"Yangilangan izoh"})
        log("PATCH","/api/community/comments/{id}/",200,r.status_code if r else 0)
        r, _ = req("DELETE",f"/api/community/comments/{CM_ID}/", token=T2)
        log("DELETE","/api/community/comments/{id}/",204,r.status_code if r else 0)

# Likes toggle
if use_post:
    r, _ = req("POST","/api/community/likes/toggle/", token=T1, data={"post":use_post})
    log("POST","/api/community/likes/toggle/",(200,201),r.status_code if r else 0, note="toggle like")
    r, _ = req("POST","/api/community/likes/toggle/", token=T1, data={"post":use_post})
    log("POST","/api/community/likes/toggle/ [unlike]",200,r.status_code if r else 0, note="toggle unlike")

r, _ = req("GET","/api/community/challenges/", token=T1)
log("GET","/api/community/challenges/",200,r.status_code if r else 0)
CH_ID = first_id(r)

r, _ = req("GET","/api/community/challenges/weekly/", token=T1)
log("GET","/api/community/challenges/weekly/",200,r.status_code if r else 0)

r, _ = req("GET","/api/community/my-challenges/", token=T1)
log("GET","/api/community/my-challenges/",200,r.status_code if r else 0)

if CH_ID:
    r, _ = req("POST","/api/community/my-challenges/", token=T1, data={"challenge":CH_ID})
    log("POST","/api/community/my-challenges/",(200,201,400),r.status_code if r else 0)
    UC_ID = jget(r,"id") if r and r.status_code in [200,201] else None
    if UC_ID:
        r, _ = req("POST",f"/api/community/my-challenges/{UC_ID}/complete/", token=T1,
                   data={"total_calories":300,"total_duration":1800})
        log("POST","/api/community/my-challenges/{id}/complete/",200,r.status_code if r else 0)

if NP_ID:
    r, _ = req("DELETE",f"/api/community/posts/{NP_ID}/", token=T1)
    log("DELETE","/api/community/posts/{id}/",204,r.status_code if r else 0)

# ── CONTENT ─────────────────────────────────────────────
print("\n  ── CONTENT ──")
r, _ = req("GET","/api/content/articles/", token=T1)
log("GET","/api/content/articles/",200,r.status_code if r else 0)
ART_ID = first_id(r)

if ART_ID:
    r, _ = req("GET",f"/api/content/articles/{ART_ID}/", token=T1)
    log("GET","/api/content/articles/{id}/",200,r.status_code if r else 0)

r, _ = req("GET","/api/content/favorites/", token=T1)
log("GET","/api/content/favorites/",200,r.status_code if r else 0)

if ART_ID:
    r, _ = req("POST","/api/content/favorites/", token=T1, data={"article":ART_ID})
    log("POST","/api/content/favorites/",(200,201,400),r.status_code if r else 0)
    FA_ID = jget(r,"id") if r and r.status_code in [200,201] else None
    if FA_ID:
        r, _ = req("DELETE",f"/api/content/favorites/{FA_ID}/", token=T1)
        log("DELETE","/api/content/favorites/{id}/",204,r.status_code if r else 0)

# ── NOTIFICATIONS ───────────────────────────────────────
print("\n  ── NOTIFICATIONS ──")
r, _ = req("GET","/api/notifications/", token=T1)
log("GET","/api/notifications/",200,r.status_code if r else 0)
NT_ID = first_id(r)

if NT_ID:
    r, _ = req("GET",f"/api/notifications/{NT_ID}/", token=T1)
    log("GET","/api/notifications/{id}/",200,r.status_code if r else 0)

r, _ = req("POST","/api/notifications/read_all/", token=T1)
log("POST","/api/notifications/read_all/",200,r.status_code if r else 0)

# ── SUPPORT ─────────────────────────────────────────────
print("\n  ── SUPPORT ──")
r, _ = req("GET","/api/support/faqs/", token=T1)
log("GET","/api/support/faqs/",200,r.status_code if r else 0)

r, _ = req("GET","/api/support/messages/", token=T1)
log("GET","/api/support/messages/",200,r.status_code if r else 0)

r, _ = req("POST","/api/support/messages/", token=T1, data={
    "message":"Qayta test: savolim bor."
})
log("POST","/api/support/messages/",(200,201),r.status_code if r else 0)

# ── SEARCH ──────────────────────────────────────────────
print("\n  ── SEARCH ──")
r, _ = req("GET","/api/search/", token=T1, params={"q":"squat","type":"all"})
log("GET","/api/search/?q=squat&type=all",200,r.status_code if r else 0)

r, _ = req("GET","/api/search/", token=T1, params={"q":"protein","type":"nutrition"})
log("GET","/api/search/?q=protein&type=nutrition",200,r.status_code if r else 0)

r, _ = req("GET","/api/search/", token=T1, params={"q":"yoga","type":"workout"})
log("GET","/api/search/?q=yoga&type=workout",200,r.status_code if r else 0)

r, _ = req("GET","/api/search/", token=T1, params={"q":"motivatsiya","type":"article"})
log("GET","/api/search/?q=motivatsiya&type=article",200,r.status_code if r else 0)

# ═══════════════════════════════════════════════════════════
# BOSQICH 2: XAVFSIZLIK TESTLARI
# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  XAVFSIZLIK TESTLARI")
print("="*70)
S = "SECURITY"

print("\n  ── Token yo'q (401 kutiladi) ──")
for method, ep in [
    ("GET",  "/api/auth/me/"),
    ("GET",  "/api/workouts/logs/"),
    ("GET",  "/api/progress/entries/"),
    ("GET",  "/api/notifications/"),
    ("GET",  "/api/community/my-challenges/"),
    ("GET",  "/api/nutrition/meal-logs/"),
]:
    r, _ = req(method, ep)
    log(method, f"{ep} [no-token]", 401, r.status_code if r else 0, section=S)

print("\n  ── Noto'g'ri / sahta token ──")
r, _ = req("GET","/api/auth/me/", token="bad.token.xyz")
log("GET","/api/auth/me/ [bad token]",401,r.status_code if r else 0, section=S)

r, _ = req("GET","/api/workouts/logs/", token="eyJhbGciOiJIUzI1NiJ9.fake.sig")
log("GET","/api/workouts/logs/ [fake token]",401,r.status_code if r else 0, section=S)

print("\n  ── Boshqa userning ob'ekti (403/404 kutiladi) ──")
r, _ = req("GET","/api/workouts/logs/", token=T1)
log1_ids = []
d = r.json() if r else {}
for it in d.get("results", []):
    log1_ids.append(it["id"])

if log1_ids:
    lid = log1_ids[0]
    r, _ = req("GET",    f"/api/workouts/logs/{lid}/", token=T2)
    log("GET",   "/api/workouts/logs/user1/ [user2]",(403,404),r.status_code if r else 0, section=S)
    r, _ = req("PATCH",  f"/api/workouts/logs/{lid}/", token=T2, data={"notes":"hack"})
    log("PATCH", "/api/workouts/logs/user1/ [user2]",(403,404),r.status_code if r else 0, section=S)
    r, _ = req("DELETE", f"/api/workouts/logs/{lid}/", token=T2)
    log("DELETE","/api/workouts/logs/user1/ [user2]",(403,404),r.status_code if r else 0, section=S)

print("\n  ── Oddiy user — trainer endpoint ──")
r, _ = req("POST","/api/workouts/workouts/", token=T1, data={
    "title":"Hack Workout","difficulty_level":"beginner","duration_minutes":5,"calories_estimated":10
})
log("POST","/api/workouts/workouts/ [user, not trainer]",(401,403),r.status_code if r else 0, section=S)

print("\n  ── Premium workout filtri ──")
r, _ = req("GET","/api/workouts/workouts/", token=T1)
d = r.json() if r else {}
premium_shown = [w for w in d.get("results",[]) if w.get("is_premium")]
log("GET","/api/workouts/workouts/ [premium filter]","HIDDEN",
    "VISIBLE" if premium_shown else "HIDDEN",
    note=f"{len(premium_shown)} ta ko'rinmoqda", section=S)

print("\n  ── SQL injection / XSS input ──")
r, _ = req("GET","/api/workouts/workouts/", token=T1, params={"search":"' OR 1=1 --"})
log("GET","/api/workouts/workouts/?search=SQLi",200,r.status_code if r else 0,
    note="ORM xavfsiz", section=S)

r, _ = req("POST","/api/community/posts/", token=T1, data={
    "title":"<script>alert('xss')</script>","content":"'; DROP TABLE users;--","category":3
})
log("POST","/api/community/posts/ [xss]",(200,201,400),r.status_code if r else 0,
    note="kiritiladi lekin escape kerak", section=S)
XSS_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if XSS_ID:
    req("DELETE",f"/api/community/posts/{XSS_ID}/", token=T1)

# ═══════════════════════════════════════════════════════════
# BOSQICH 3: VALIDATION TESTLARI
# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  VALIDATION TESTLARI")
print("="*70)
V = "VALIDATION"

print("\n  ── Bo'sh body ──")
for ep in ["/api/auth/register/","/api/workouts/logs/",
           "/api/progress/entries/","/api/nutrition/meal-logs/"]:
    method = "POST"
    token = None if ep == "/api/auth/register/" else T1
    r, _ = req(method, ep, token=token, data={})
    log(method, f"{ep} [empty]", 400, r.status_code if r else 0, section=V)

print("\n  ── Login xatolari ──")
r, _ = req("POST","/api/auth/login/", data={"username":"user1","password":"WRONG"})
log("POST","/api/auth/login/ [wrong pass]",401,r.status_code if r else 0, section=V)

r, _ = req("POST","/api/auth/login/", data={"username":"notexist@x.com","password":"Test12345!"})
log("POST","/api/auth/login/ [no user]",401,r.status_code if r else 0, section=V)

print("\n  ── Noto'g'ri UUID ──")
fake = "00000000-0000-0000-0000-000000000000"
r, _ = req("GET",f"/api/workouts/workouts/{fake}/", token=T1)
log("GET","/api/workouts/workouts/[bad-uuid]/",404,r.status_code if r else 0, section=V)
r, _ = req("GET",f"/api/progress/entries/{fake}/", token=T1)
log("GET","/api/progress/entries/[bad-uuid]/",404,r.status_code if r else 0, section=V)

print("\n  ── Noto'g'ri qiymatlar ──")
r, _ = req("POST","/api/progress/entries/", token=T1, data={"date":"not-a-date","weight_kg":"abc"})
log("POST","/api/progress/entries/ [bad date]",400,r.status_code if r else 0, section=V)

r, _ = req("POST","/api/workouts/logs/", token=T1, data={
    "workout":WID,"started_at":datetime.now().isoformat(),"rating":99
})
# rating validation complete() da ishlaydi, create da emas
s = r.status_code if r else 0
log("POST","/api/workouts/logs/ [rating=99]",(201,400),s,
    note="rating complete() da validate qilinadi", section=V)
BAD_LOG_ID = jget(r,"id") if r and r.status_code in [200,201] else None
if BAD_LOG_ID:
    req("DELETE",f"/api/workouts/logs/{BAD_LOG_ID}/", token=T1)

print("\n  ── Duplicate unique_together ──")
r, _ = req("POST","/api/workouts/favorites/", token=T1, data={"workout":WID})
r2, _ = req("POST","/api/workouts/favorites/", token=T1, data={"workout":WID})
log("POST","/api/workouts/favorites/ [dup]",400,r2.status_code if r2 else 0,
    note="unique_together", section=V)
if r and r.status_code in [200,201]:
    req("DELETE",f"/api/workouts/favorites/{jget(r,'id')}/", token=T1)
if r2 and r2.status_code in [200,201]:
    req("DELETE",f"/api/workouts/favorites/{jget(r2,'id')}/", token=T1)

print("\n  ── UserChallenge duplicate join ──")
if CH_ID:
    r, _ = req("POST","/api/community/my-challenges/", token=T2, data={"challenge":CH_ID})
    r2, _ = req("POST","/api/community/my-challenges/", token=T2, data={"challenge":CH_ID})
    log("POST","/api/community/my-challenges/ [dup join]",400,r2.status_code if r2 else 0,
        note="validate_challenge", section=V)

print("\n  ── password2 mos kelmasa ──")
r, _ = req("POST","/api/auth/register/", data={
    "email":"mismatch@test.com","nickname":"mismatch","full_name":"M",
    "password":"Test12345!","password2":"DIFFERENT!"
})
log("POST","/api/auth/register/ [pass mismatch]",400,r.status_code if r else 0, section=V)

# ═══════════════════════════════════════════════════════════
# BOSQICH 4: FILTER / SEARCH / PAGINATION
# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  FILTER / SEARCH / PAGINATION")
print("="*70)
F = "FILTER"

filters = [
    ("GET","/api/workouts/workouts/",{"difficulty_level":"beginner"},"difficulty filter"),
    ("GET","/api/workouts/workouts/",{"is_training_of_the_day":"true"},"training_of_the_day filter"),
    ("GET","/api/workouts/workouts/",{"is_premium":"false"},"premium=false filter"),
    ("GET","/api/workouts/exercises/",{"difficulty_level":"beginner"},"exercise difficulty"),
    ("GET","/api/nutrition/recipes/",{"meal_type":"breakfast"},"meal_type filter"),
    ("GET","/api/nutrition/meal-logs/",{"meal_type":"breakfast"},"meal_log filter"),
    ("GET","/api/progress/entries/",{"date":str(date.today())},"date filter"),
    ("GET","/api/progress/entries/charts/",{"period":"week"},"chart period=week"),
    ("GET","/api/progress/entries/charts/",{"period":"year"},"chart period=year"),
    ("GET","/api/community/posts/",{"category":"3"},"post category filter"),
    ("GET","/api/workouts/workouts/",{"search":"Yoga"},"workout search"),
    ("GET","/api/workouts/exercises/",{"search":"Push"},"exercise search"),
    ("GET","/api/community/posts/",{"search":"mashq"},"post search"),
    ("GET","/api/content/articles/",{"search":"protein"},"article search"),
    ("GET","/api/search/",{"q":"squat","type":"all"},"global search"),
]
for method, ep, params, note in filters:
    r, _ = req(method, ep, token=T1, params=params)
    d = r.json() if r else {}
    cnt = d.get("count","?") if isinstance(d,dict) else "?"
    log(method, f"{ep}[{note}]", 200, r.status_code if r else 0,
        note=f"count={cnt}", section=F)

print("\n  ── Pagination ──")
for ep in ["/api/workouts/workouts/","/api/community/posts/","/api/content/articles/"]:
    r, _ = req("GET", ep, token=T1)
    d = r.json() if r else {}
    has_p = isinstance(d,dict) and "count" in d and "results" in d
    log("GET", f"{ep} [pagination]", 200, r.status_code if r else 0,
        note="HA" if has_p else "YOQ", section=F)

# ═══════════════════════════════════════════════════════════
# BOSQICH 5: RUXSATLAR MATRITSASI
# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  RUXSATLAR MATRITSASI")
print("="*70)
P = "PERMISSIONS"

print("\n  ── Anonymous read endpointlar (200) ──")
for ep in ["/api/workouts/categories/","/api/workouts/workouts/","/api/workouts/exercises/",
           "/api/nutrition/recipes/","/api/community/posts/","/api/community/challenges/",
           "/api/content/articles/","/api/support/faqs/"]:
    r, _ = req("GET", ep)
    log("GET", f"{ep} [anon]", 200, r.status_code if r else 0, note="anon read", section=P)

print("\n  ── Anonymous write (401) ──")
for method, ep, data in [
    ("POST","/api/workouts/workouts/",{"title":"x","difficulty_level":"beginner","duration_minutes":5,"calories_estimated":10}),
    ("POST","/api/community/posts/",  {"title":"x","content":"x","category":3}),
    ("GET", "/api/notifications/",   None),
    ("GET", "/api/auth/me/",         None),
]:
    r, _ = req(method, ep, data=data)
    log(method, f"{ep} [anon write]", 401, r.status_code if r else 0, section=P)

print("\n  ── User vs Trainer ──")
r, _ = req("POST","/api/workouts/workouts/", token=T1, data={
    "title":"User hack","difficulty_level":"beginner","duration_minutes":5,"calories_estimated":10
})
log("POST","/api/workouts/workouts/ [user]",(401,403),r.status_code if r else 0,
    note="user yarata olmaydi", section=P)

r, _ = req("POST","/api/workouts/workouts/", token=TT, data={
    "title":"Trainer OK","difficulty_level":"beginner","duration_minutes":10,"calories_estimated":50
})
log("POST","/api/workouts/workouts/ [trainer]",(200,201),r.status_code if r else 0,
    note="trainer yarata oladi", section=P)
T_WID = jget(r,"id") if r and r.status_code in [200,201] else None
if T_WID:
    req("DELETE",f"/api/workouts/workouts/{T_WID}/", token=TT)

print("\n  ── Article admin-only write ──")
r, _ = req("POST","/api/content/articles/", token=T1, data={
    "title":"User tries","content":"content","published_at":datetime.now().isoformat()
})
log("POST","/api/content/articles/ [user, not admin]",(401,403),r.status_code if r else 0,
    note="IsAdminOrReadOnly", section=P)

# ═══════════════════════════════════════════════════════════
# BOSQICH 6: BUSINESS FLOW TESTLARI
# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  BUSINESS FLOW TESTLARI")
print("="*70)
FL = "FLOW"

print("\n  Flow 1: Register → Login → Onboarding → Profile")
r, _ = req("POST","/api/auth/register/", data={
    "email":"flow2026@test.com","nickname":"flow2026","full_name":"Flow 2026",
    "password":"FlowPass123!","password2":"FlowPass123!"
})
log("POST","Register",(200,201),r.status_code if r else 0, section=FL)
if r and r.status_code in [200,201]:
    rl, _ = req("POST","/api/auth/login/", data={"username":"flow2026","password":"FlowPass123!"})
    FT = rl.json().get("access") if rl and rl.status_code==200 else None
    if FT:
        r, _ = req("POST","/api/auth/onboarding/", token=FT, data={
            "gender":"female","fitness_level":"beginner","primary_goal":"shape_body",
            "height_cm":165,"weight_kg":58
        })
        log("POST","Onboarding",200,r.status_code if r else 0, section=FL)
        r, _ = req("GET","/api/auth/me/", token=FT)
        log("GET","Profile check",200,r.status_code if r else 0, section=FL)

print("\n  Flow 2: Workout → Log → Complete")
r, _ = req("GET","/api/workouts/workouts/", token=T1)
fw_id = first_id(r)
log("GET","Workout list",200,r.status_code if r else 0, section=FL)
if fw_id:
    r, _ = req("POST","/api/workouts/logs/", token=T1,
               data={"workout":fw_id,"started_at":datetime.now().isoformat()})
    log("POST","Workout log start",(200,201),r.status_code if r else 0, section=FL)
    flog = jget(r,"id") if r and r.status_code in [200,201] else None
    if flog:
        r, _ = req("POST",f"/api/workouts/logs/{flog}/complete/", token=T1, data={
            "completed_at":datetime.now().isoformat(),
            "duration_seconds":2700,"rating":4,"calories_burned":310
        })
        log("POST","Workout log complete",200,r.status_code if r else 0, section=FL)

print("\n  Flow 3: Meal plan → Meal log → Summary")
r, _ = req("PATCH","/api/nutrition/preferences/", token=T1, data={
    "dietary_preferences":[],"allergies":[],"meal_types":["breakfast","lunch","dinner"],
    "caloric_goal":2200,"number_of_servings":3
})
log("PATCH","Meal pref update",200,r.status_code if r else 0, section=FL)
r, _ = req("POST","/api/nutrition/meal-plans/", token=T1, data={"date":str(date.today()-timedelta(days=1))})
log("POST","Meal plan generate",(200,201),r.status_code if r else 0, section=FL)
if RCP_ID:
    r, _ = req("POST","/api/nutrition/meal-logs/", token=T1, data={
        "recipe":RCP_ID,"meal_type":"lunch","quantity":"1.00","logged_at":datetime.now().isoformat()
    })
    log("POST","Meal log",(200,201),r.status_code if r else 0, section=FL)
r, _ = req("GET","/api/nutrition/meal-logs/summary/", token=T1, params={"date":str(date.today())})
log("GET","Meal summary",(200,404),r.status_code if r else 0, section=FL)

print("\n  Flow 4: Challenge join → Complete")
r, _ = req("GET","/api/community/challenges/", token=T1)
log("GET","Challenge list",200,r.status_code if r else 0, section=FL)
cid = first_id(r)
if cid:
    r, _ = req("POST","/api/community/my-challenges/", token=T1, data={"challenge":cid})
    log("POST","Challenge join",(200,201,400),r.status_code if r else 0,
        note="400=already joined", section=FL)
    ucid = jget(r,"id") if r and r.status_code in [200,201] else None
    if ucid:
        r, _ = req("POST",f"/api/community/my-challenges/{ucid}/complete/", token=T1,
                   data={"total_calories":250,"total_duration":1200})
        log("POST","Challenge complete",200,r.status_code if r else 0, section=FL)

print("\n  Flow 5: Like toggle")
r, _ = req("GET","/api/community/posts/", token=T1)
fpid = first_id(r)
if fpid:
    r, _ = req("POST","/api/community/likes/toggle/", token=T2, data={"post":fpid})
    log("POST","Like toggle (add)",(200,201),r.status_code if r else 0, section=FL)
    r, _ = req("POST","/api/community/likes/toggle/", token=T2, data={"post":fpid})
    log("POST","Like toggle (remove)",200,r.status_code if r else 0, section=FL)

print("\n  Flow 6: Progress + Charts")
r, _ = req("POST","/api/progress/entries/", token=T2, data={
    "date":str(date.today()-timedelta(days=500)),"weight_kg":"68.00","notes":"flow test"
})
log("POST","Progress entry",(200,201),r.status_code if r else 0, section=FL)
for period in ["week","month","year"]:
    r, _ = req("GET","/api/progress/entries/charts/", token=T2, params={"period":period})
    log("GET",f"Charts [{period}]",200,r.status_code if r else 0, section=FL)

print("\n  Flow 7: Forum post → comment → like")
r, _ = req("POST","/api/community/posts/", token=T2, data={
    "title":"Flow Forum Post","content":"Flow test forum.","category":3
})
log("POST","Forum post",(200,201),r.status_code if r else 0, section=FL)
fpst = jget(r,"id") if r and r.status_code in [200,201] else None
if fpst:
    r, _ = req("POST","/api/community/comments/", token=T1,
               data={"post":fpst,"content":"Flow izoh"})
    log("POST","Forum comment",(200,201),r.status_code if r else 0, section=FL)
    r, _ = req("POST","/api/community/likes/toggle/", token=T1, data={"post":fpst})
    log("POST","Forum like toggle",(200,201),r.status_code if r else 0, section=FL)
    req("DELETE",f"/api/community/posts/{fpst}/", token=T2)

print("\n  Flow 8: Notifications read_all")
r, _ = req("GET","/api/notifications/", token=T1)
unread = len([n for n in r.json().get("results",[]) if not n.get("is_read")]) if r else 0
log("GET","Notif list (unread check)",200,r.status_code if r else 0,
    note=f"unread={unread}", section=FL)
r, _ = req("POST","/api/notifications/read_all/", token=T1)
log("POST","Notif read_all",200,r.status_code if r else 0, section=FL)

print("\n  Flow 9: Support message")
r, _ = req("POST","/api/support/messages/", token=T1, data={"message":"Flow support savolim."})
log("POST","Support message",(200,201),r.status_code if r else 0, section=FL)

# ═══════════════════════════════════════════════════════════
# BOSQICH 7: PERFORMANCE
# ═══════════════════════════════════════════════════════════
print("\n" + "="*70)
print("  PERFORMANCE (10 so'rov)")
print("="*70)
PERF = "PERFORMANCE"

for ep in ["/api/workouts/workouts/","/api/community/posts/","/api/notifications/"]:
    times = []
    for _ in range(10):
        _, t = req("GET", ep, token=T1)
        times.append(t)
    avg = round(sum(times)/len(times), 3)
    mx  = round(max(times), 3)
    status_note = "SEKIN!" if avg > 1.0 else "OK"
    print(f"  {ep}: avg={avg}s max={mx}s [{status_note}]")
    log("GET", f"{ep}[x10]", "< 1s", f"{avg}s",
        note=f"max={mx}s", section=PERF)

# ═══════════════════════════════════════════════════════════
# YAKUNIY NATIJA
# ═══════════════════════════════════════════════════════════
total = ok_count + fail_count
coverage = round(ok_count/total*100, 1) if total else 0

print("\n" + "="*70)
print("  YAKUNIY HISOBOT")
print("="*70)

sections = {}
for r_ in results:
    s = r_["section"]
    if s not in sections:
        sections[s] = {"ok":0,"fail":0,"fails":[]}
    if r_["passed"]: sections[s]["ok"] += 1
    else:
        sections[s]["fail"] += 1
        sections[s]["fails"].append(r_)

print(f"\n  Jami: {total} | OK: {ok_count} | FAIL: {fail_count} | Coverage: {coverage}%\n")
for s, d in sections.items():
    t = d["ok"]+d["fail"]
    print(f"  [{s}] OK={d['ok']}/{t}" + (f" FAIL={d['fail']}" if d["fail"] else ""))

print("\n  ── FAIL bo'lgan testlar ──")
fails = [r_ for r_ in results if not r_["passed"]]
if not fails:
    print("  Hech qanday FAIL yo'q!")
else:
    for f in fails:
        print(f"  ✗ [{f['section']}] {f['method']} {f['endpoint']}")
        print(f"       exp={f['expected']} got={f['got']}  {f['note']}")

# JSON saqlash
with open("test_results.json","w",encoding="utf-8") as fp:
    json.dump({
        "summary":{"total":total,"ok":ok_count,"fail":fail_count,"coverage_pct":coverage},
        "sections":{k:{"ok":v["ok"],"fail":v["fail"]} for k,v in sections.items()},
        "failures":[{"section":x["section"],"method":x["method"],"endpoint":x["endpoint"],
                     "expected":str(x["expected"]),"got":str(x["got"]),"note":x["note"]}
                    for x in fails],
        "all_results":[{"section":x["section"],"method":x["method"],"endpoint":x["endpoint"],
                        "passed":x["passed"],"expected":str(x["expected"]),
                        "got":str(x["got"]),"note":x["note"]}
                       for x in results]
    }, fp, ensure_ascii=False, indent=2)
print("\n  Natijalar: test_results.json ga saqlandi.")
print("="*70)
