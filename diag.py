"""Haqiqiy API xatolarini diagnostika qilish"""
import requests, json
from datetime import date, datetime

BASE = "http://127.0.0.1:8000"

r = requests.post(f"{BASE}/api/auth/login/", json={"username":"user1","password":"Test12345!"})
T1 = r.json()["access"]
r = requests.post(f"{BASE}/api/auth/login/", json={"username":"user2","password":"Test12345!"})
T2 = r.json()["access"]
H1 = {"Authorization": f"Bearer {T1}", "Content-Type": "application/json"}
H2 = {"Authorization": f"Bearer {T2}", "Content-Type": "application/json"}

def check(label, r):
    try:
        body = r.json()
    except:
        body = r.text[:200]
    print(f"  [{r.status_code}] {label}")
    if r.status_code not in (200,201,204):
        print(f"       {json.dumps(body, ensure_ascii=False)[:200]}")
    return r

print("=== 1. Register (email allaqachon mavjud bo'lsa ham test) ===")
check("register new", requests.post(f"{BASE}/api/auth/register/", json={
    "email":"diag2026new@test.com","nickname":"diag2026new",
    "full_name":"Diag","password":"DiagPass123!","password2":"DiagPass123!"
}))

print("\n=== 2. Goal complete ===")
r = requests.get(f"{BASE}/api/auth/goals/", headers=H1)
goals = r.json().get("results", [])
if goals:
    gid = goals[0]["id"]
    check(f"goal complete {gid}", requests.post(f"{BASE}/api/auth/goals/{gid}/complete/", headers=H1))
else:
    print("  goal yo'q")

print("\n=== 3. FavoriteWorkout POST ===")
r = requests.get(f"{BASE}/api/workouts/workouts/", headers=H1)
wid = r.json()["results"][0]["id"]
check("fav workout (workout field)", requests.post(f"{BASE}/api/workouts/favorites/", headers=H1, json={"workout": wid}))

print("\n=== 4. FavoriteRecipe POST ===")
r = requests.get(f"{BASE}/api/nutrition/recipes/", headers=H1)
rid = r.json()["results"][0]["id"]
check("fav recipe (recipe field)", requests.post(f"{BASE}/api/nutrition/favorites/", headers=H1, json={"recipe": rid}))

print("\n=== 5. UserChallenge POST ===")
r = requests.get(f"{BASE}/api/community/challenges/", headers=H1)
cids = [c["id"] for c in r.json().get("results",[])]
# user1 ning qaysi challenge ga join qilmagani
r2 = requests.get(f"{BASE}/api/community/my-challenges/", headers=H1)
joined = {uc["challenge"] for uc in r2.json().get("results",[])}
new_cid = next((c for c in cids if c not in joined), None)
print(f"  Mavjud challenges: {cids}")
print(f"  User1 joined: {joined}")
print(f"  Yangi join qilish uchun: {new_cid}")
if new_cid:
    check("my-challenge join", requests.post(f"{BASE}/api/community/my-challenges/", headers=H1, json={"challenge": new_cid}))
else:
    print("  Barcha challenge larga join qilingan — 400 kutiladi")
    check("my-challenge dup", requests.post(f"{BASE}/api/community/my-challenges/", headers=H1, json={"challenge": cids[0]}))

print("\n=== 6. Notifications GET ===")
check("notifications list", requests.get(f"{BASE}/api/notifications/", headers=H1))

print("\n=== 7. No-token => 401 test ===")
check("GET /api/auth/me/ no token", requests.get(f"{BASE}/api/auth/me/"))
check("GET /api/workouts/logs/ no token", requests.get(f"{BASE}/api/workouts/logs/"))

print("\n=== 8. User POST workout (403 kutiladi) ===")
check("POST workout [user]", requests.post(f"{BASE}/api/workouts/workouts/", headers=H1, json={
    "title":"Hack","difficulty_level":"beginner","duration_minutes":5,"calories_estimated":10
}))

print("\n=== 9. Bad token 401 ===")
check("bad token", requests.get(f"{BASE}/api/auth/me/", headers={"Authorization":"Bearer bad.token.xyz"}))

print("\n=== 10. Cross-user object access ===")
r = requests.get(f"{BASE}/api/workouts/logs/", headers=H1)
log_ids = [l["id"] for l in r.json().get("results",[])]
print(f"  user1 log ids: {log_ids[:2]}")
if log_ids:
    check(f"user2 GET user1 log", requests.get(f"{BASE}/api/workouts/logs/{log_ids[0]}/", headers=H2))
    check(f"user2 DELETE user1 log", requests.delete(f"{BASE}/api/workouts/logs/{log_ids[0]}/", headers=H2))

print("\n=== 11. Empty body => 400 ===")
check("register empty", requests.post(f"{BASE}/api/auth/register/", headers={"Content-Type":"application/json"}, json={}))
check("login wrong pass", requests.post(f"{BASE}/api/auth/login/", json={"username":"user1","password":"WRONG"}))
check("bad uuid", requests.get(f"{BASE}/api/workouts/workouts/00000000-0000-0000-0000-000000000000/", headers=H1))
check("bad date progress", requests.post(f"{BASE}/api/progress/entries/", headers=H1, json={"date":"not-a-date","weight_kg":"abc"}))

print("\n=== 12. FavoriteWorkout duplicate ===")
r1 = requests.post(f"{BASE}/api/workouts/favorites/", headers=H1, json={"workout": wid})
r2 = requests.post(f"{BASE}/api/workouts/favorites/", headers=H1, json={"workout": wid})
check("dup fav 1st", r1)
check("dup fav 2nd (400 kutiladi)", r2)
# tozalash
for resp in [r1, r2]:
    if resp.status_code in [200,201]:
        fid = resp.json().get("id")
        if fid:
            requests.delete(f"{BASE}/api/workouts/favorites/{fid}/", headers=H1)

print("\n=== 13. Article admin write ===")
check("article POST [user]", requests.post(f"{BASE}/api/content/articles/", headers=H1, json={
    "title":"test","content":"test","published_at":datetime.now().isoformat()
}))

print("\n=== 14. Like toggle ikkinchi marta ===")
r = requests.get(f"{BASE}/api/community/posts/", headers=H1)
post_id = r.json()["results"][0]["id"]
r1 = requests.post(f"{BASE}/api/community/likes/toggle/", headers=H2, json={"post": post_id})
r2 = requests.post(f"{BASE}/api/community/likes/toggle/", headers=H2, json={"post": post_id})
check("like add", r1)
check("like remove (200 kutiladi)", r2)
