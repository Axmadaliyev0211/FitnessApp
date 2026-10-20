import requests

BASE = "http://127.0.0.1:8000"

# Login
token = requests.post(
    f"{BASE}/api/auth/login/",
    json={"username": "user1", "password": "Test12345!"}
).json()["access"]
auth = {"Authorization": f"Bearer {token}"}

print("=" * 58)
print("  Accept-Language header bilan real API javoblari")
print("=" * 58)

print("\n--- Workout /api/workouts/workouts/ ---")
for lang in ["uz", "en", "ru"]:
    h = {**auth, "Accept-Language": lang}
    r = requests.get(f"{BASE}/api/workouts/workouts/", headers=h)
    d = r.json()
    first = d["results"][0] if d.get("results") else {}
    title = first.get("title", "")
    desc  = str(first.get("description", ""))[:40]
    print(f"  [{lang}] title={title!r}  desc={desc!r}")

print("\n--- Recipe /api/nutrition/recipes/ ---")
for lang in ["uz", "en", "ru"]:
    h = {**auth, "Accept-Language": lang}
    r = requests.get(f"{BASE}/api/nutrition/recipes/", headers=h)
    d = r.json()
    first = d["results"][0] if d.get("results") else {}
    print(f"  [{lang}] title={first.get('title')!r}")

print("\n--- FAQ /api/support/faqs/ ---")
for lang in ["uz", "en", "ru"]:
    h = {"Accept-Language": lang}
    r = requests.get(f"{BASE}/api/support/faqs/", headers=h)
    d = r.json()
    results = d.get("results", d) if isinstance(d, dict) else d
    first = results[0] if results else {}
    q = str(first.get("question", ""))[:55]
    print(f"  [{lang}] question={q!r}")

print("\n--- Article /api/content/articles/ ---")
for lang in ["uz", "en", "ru"]:
    h = {**auth, "Accept-Language": lang}
    r = requests.get(f"{BASE}/api/content/articles/", headers=h)
    d = r.json()
    first = d["results"][0] if d.get("results") else {}
    print(f"  [{lang}] title={first.get('title')!r}")

print("\n--- Challenge /api/community/challenges/ ---")
for lang in ["uz", "en", "ru"]:
    h = {"Accept-Language": lang}
    r = requests.get(f"{BASE}/api/community/challenges/", headers=h)
    d = r.json()
    first = d["results"][0] if d.get("results") else {}
    print(f"  [{lang}] title={first.get('title')!r}")
