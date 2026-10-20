# PythonAnywhere ga Joylash Yo'riqnomasi

## 1. Tayyorgarlik

### 1.1. Yangi SECRET_KEY generatsiya qilish

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 1.2. GitHub ga yuklash (tavsiya)

```bash
cd c:\Users\Notbukom\Desktop\FitnesApp
git init
git add .
git commit -m "PythonAnywhere ga tayyor"
git branch -M main
git remote add origin https://github.com/USERNAME/FitnesApp.git
git push -u origin main
```

> GitHub ga yuklamasangiz ham bo'ladi — ZIP fayl orqali yuklash mumkin.

---

## 2. PythonAnywhere hisobini yaratish

1. **pythonanywhere.com** ga kiring
2. **"Create a Beginner account"** (bepul plan)
3. Username: `sizning_username` (masalan: `fitnesapp`)
4. Email tasdiqlang

---

## 3. Loyihani yuklash

### Variant A: GitHub dan (tavsiya)

PythonAnywhere **Dashboard** → **Consoles** → **Bash** oching:

```bash
git clone https://github.com/USERNAME/FitnesApp.git ~/FitnesApp
```

### Variant B: ZIP fayl

1. Loyiha papkasini ZIP qiling
2. PythonAnywhere **Files** bo'limiga yuklang
3. Bash konsolda:
```bash
cd ~
unzip FitnesApp.zip
```

---

## 4. Virtual Environment

PythonAnywhere **Dashboard** → **Consoles** → **Bash**:

```bash
cd ~/FitnesApp
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **Muhim:** PythonAnywhere da `channels` va `daphne` o'rnatiladi lekin
> `ON_PYTHONANYWHERE=True` bo'lgani uchun faqat WSGI rejimida ishlaydi.

---

## 5. .env fayl yaratish

Bash konsolda:

```bash
cd ~/FitnesApp
cat > .env << 'EOF'
SECRET_KEY="YANGI_SECRET_KEY_BU_YERGA"
DEBUG=False
ALLOWED_HOSTS=fitnesapp.pythonanywhere.com
ON_PYTHONANYWHERE=True
FRONTEND_URL=https://fitnesapp.pythonanywhere.com
EOF
```

> `ALLOWED_HOSTS` va `FRONTEND_URL` da `fitnesapp` ni o'z username ingizga almashtiring!

---

## 6. Migratsiya va Static Files

```bash
cd ~/FitnesApp
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## 7. Web App sozlamasi

PythonAnywhere **Dashboard** → **Web** → **Add a new web app**:

1. **Manual configuration**
2. **Python 3.11**
3. **Working directory:** `/home/USERNAME/FitnesApp`

### 7.1. WSGI faylni tahrirlash

**Web** bo'limida **WSGI configuration file** linkini bosing va quyidagicha tahrirlang:

```python
import os
import sys

# Loyiha papkasi
path = '/home/USERNAME/FitnesApp'
if path not in sys.path:
    sys.path.append(path)

# .env fayl uchun — loyiha papkasidan o'qiydi
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# decouple .env faylni topishi uchun CWD
os.chdir(path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

> `USERNAME` ni o'z username ingizga almashtiring!

### 7.2. Virtual Environment

**Web** bo'limida **Virtualenv** qismida:

```
/home/USERNAME/FitnesApp/.venv
```

### 7.3. Static Files

**Web** bo'limida **Static files** qismida 2 ta qator qo'shing:

| URL | Directory |
|---|---|
| `/static/` | `/home/USERNAME/FitnesApp/staticfiles/` |
| `/media/` | `/home/USERNAME/FitnesApp/media/` |

---

## 8. Web App ni restart qilish

**Web** bo'limida yuqori o'ng burchakda **Reload** tugmasini bosing.

---

## 9. Tekshirish

Brauzerda oching:

```
https://USERNAME.pythonanywhere.com/api/docs/
```

Swagger UI ochilishi kerak.

API test uchun:

```
https://USERNAME.pythonanywhere.com/api/auth/login/
```

POST so'rov yuboring:

```json
{
    "username": "siz_login",
    "password": "siz_parol"
}
```

---

## 10. Muhim eslatmalar

### 10.1. Nima ishlaydi ✅

- Barcha REST API endpointlar
- JWT autentifikatsiya
- 3 til (uz/en/ru) modeltranslation
- Filter/Search/Pagination
- Swagger API docs
- Admin panel

### 10.2. Nima ishlamaydi ❌

- **WebSocket** — `daphne`/`channels` PythonAnywhere da WSGI rejimida ishlamaydi.
  `SupportReplyView` REST API orqali ishlaydi, lekin real-time push yo'q.
  Mijoz (frontend) poll qilib yangi xabarlarni olishi kerak.

### 10.3. Bepul plan cheklovlari

| Cheklov | Qiymat |
|---|---|
| CPU | 2000 soniya/24 soat |
| Disk | 512 MB |
| Traffic | 2.5 GB/oy |
| Custom domains | Yo'q |
| HTTPS | `*.pythonanywhere.com` da bor |

### 10.4. MySQL ga o'tish (tavsiya)

Bepul plan SQLite bilan ishlaydi, lekin MySQL tavsiya etiladi:

```bash
pip install PyMySQL
```

`config/settings.py` da DATABASES ni o'zgartiring:

```python
import pymysql
pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'USERNAME$fitnesapp',
        'USER': 'USERNAME',
        'PASSWORD': 'SIZNING_DB_PAROL',
        'HOST': 'USERNAME.mysql.pythonanywhere-services.com',
    }
}
```

---

## 11. Xatolik yuzaga kelsa

### 11.1. Error log

**Web** bo'limida **Error log** linkini bosing.

### 11.2. Tez-tez uchraydigan xatolar

| Xato | Yechim |
|---|---|
| `ModuleNotFoundError` | `pip install -r requirements.txt` ni qaytadan ishga tushiring |
| `SECRET_KEY not found` | `.env` fayl loyiha papkasida ekanligini tekshiring |
| `DisallowedHost` | `.env` da `ALLOWED_HOSTS` ga username.pythonanywhere.com qo'shing |
| `Static files 404` | `python manage.py collectstatic` + Web tab da static maps ni tekshiring |
| `channels import error` | `ON_PYTHONANYWHERE=True` ekanligini tekshiring |

### 11.3. .env fayl topilmasa

PythonAnywhere da `.env` fayl decouple tomonidan topilishi uchun
WSGI fayl da `os.chdir(path)` qatorini qo'shgan bo'lishingiz kerak.

---
 
*Yo'riqnoma: 29 Sentabr 2026*
