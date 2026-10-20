import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth import get_user_model, authenticate
User = get_user_model()

# user1 — username va nickname ni tuzat, parolni yangilab qo'y
u1 = User.objects.get(email='user1@test.com')
u1.username = 'user1'
u1.nickname = 'user1'
u1.set_password('Test12345!')
u1.save()
print(f"user1: username={u1.username}, active={u1.is_active}")

# user2
u2 = User.objects.get(email='user2@test.com')
u2.set_password('Test12345!')
u2.save()
print(f"user2: username={u2.username}, active={u2.is_active}")

# trainer
u3 = User.objects.get(email='trainer@test.com')
u3.set_password('Test12345!')
u3.save()
print(f"trainer: username={u3.username}, active={u3.is_active}")

# Login tekshiruvi
for uname in ['user1','user2','trainer']:
    a = authenticate(username=uname, password='Test12345!')
    status = "OK" if a else "FAIL"
    print(f"  login [{uname}]: {status}")
