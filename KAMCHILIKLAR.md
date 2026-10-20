# FitnesApp — To'liq Loyiha Tahlili va Kamchiliklar Hisoboti

> **Tahlil sanasi:** 17 Sentyabr 2026  
> **Django versiyasi:** 5.0.1  
> **Test usuli:** Barcha fayllar to'liq o'qildi + `manage.py shell` orqali real DB testlari + `manage.py check --deploy`  
> **Jami topilgan kamchiliklar: 42 ta**

---

## Jiddiylik darajalari

| Belgi | Daraja | Ta'rif |
|---|---|---|
| 🔴 | **Kritik** | Funksiya ishlamaydi yoki xavfsizlik xatari bor |
| 🟠 | **Jiddiy** | Ma'lumot noto'g'ri saqlanadi / mantiq buzilgan |
| 🟡 | **O'rta** | Dizayn muammosi yoki potensial runtime xato |
| 🔵 | **Tavsiya** | Yaxshi amaliyot uchun tavsiya |

---

## 🔴 KRITIK KAMCHILIKLAR

---

### 🔴 #1 — `ForgotPasswordView` email yubormasdan token'ni HTTP response'da qaytaradi

**Fayl:** `users/views.py`  
**Test:** `TEST9 ForgotPasswordView sends email: False` | `TEST9 Returns token in response: True`

**Muammo:**
```python
class ForgotPasswordView(APIView):
    def post(self, request):
        ...
        reset_link = f"https://yourfrontend.com/reset-password/?uid={uid}&token={token}"
        return Response({
            "uid": uid,
            "token": token,      # ← TOKEN HTTP RESPONSE DA OCHIQ!
            "reset_link": reset_link
        })
```

Parolni tiklash tokeni foydalanuvchiga **email orqali** yuborilishi kerak. Hozirgi holatda token HTTP response'da qaytariladi — bu katta xavfsizlik kamchiligi. Hech qanday email jo'natish kodi yo'q (`send_mail`, `EmailMessage` yo'q).

**Oqibat:** Istalgan kishi boshqaning emailini bilsa, API orqali to'g'ridan-to'g'ri token olishi va parolni o'zgartirishi mumkin.

---

### 🔴 #2 — `DeleteAccountView` JWT tokenlarini bekor qilmaydi

**Fayl:** `users/views.py`  
**Test:** `TEST12 DeleteAccountView blacklists JWT tokens: False`

**Muammo:**
```python
class DeleteAccountView(APIView):
    def post(self, request):
        user.is_active = False
        user.save()
        # ← JWT token hali valid! Logout qilinmaydi!
```

`is_active=False` qilingandan keyin ham foydalanuvchining JWT access token muddati tugamaguncha (`ACCESS_TOKEN_LIFETIME = timedelta(days=1)`) ishlaydi. Token blacklistga qo'shilmaydi.

---

### 🔴 #3 — `FavoriteWorkoutSerializer` — `workout_id` write field yo'q, POST da `IntegrityError`

**Fayl:** `workouts/serializers.py`, `workouts/views.py`  
**Test:** `TEST32 workout in validated_data: False` — `IntegrityError` chiqadi

**Muammo:**
```python
class FavoriteWorkoutSerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer(read_only=True)  # ← faqat o'qish!
    class Meta:
        fields = ('id', 'workout', 'added_at')   # workout_id yo'q
```

```python
# views.py
def perform_create(self, serializer):
    serializer.save(user=self.request.user)      # workout berilmaydi
```

`workout` field `read_only=True` bo'lgani uchun POST so'rovdagi `workout_id` ignored. `perform_create` esa faqat `user=request.user` qo'shadi. `FavoriteWorkout.workout NOT NULL` constraint buzilib `IntegrityError` kelib chiqadi.

---

### 🔴 #4 — `FavoriteRecipeSerializer` — xuddi shu muammo (`recipe_id` yo'q)

**Fayl:** `nutrition/serializers.py`, `nutrition/views.py`  
**Test:** `TEST24 FavoriteRecipeSerializer with recipe id valid: True` — lekin `recipe_id` validated_data da yo'q

**Muammo:**
```python
class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)  # ← faqat o'qish!
    class Meta:
        fields = ('id', 'recipe', 'created_at') # recipe_id yo'q
```

`perform_create(serializer)` faqat `user=request.user` qo'shadi. `recipe` ham qo'shilmaydi → `IntegrityError`.

---

### 🔴 #5 — `GlobalSearchView` — duplicate Workout query va premium filter ishlamaydi

**Fayl:** `core/views.py`  
**Test:** `TEST26 GlobalSearch Workout.objects.filter calls: 2`

**Muammo:**
```python
def get(self, request):
    if search_type in ['all', 'workout']:
        workouts = Workout.objects.filter(...)[:10]
        results["workouts"] = WorkoutSerializer(workouts, ...).data   # ← BIRINCHI QUERY

    # ... pastda alohida query
    workouts = Workout.objects.filter(...)                             # ← IKKINCHI QUERY
    if not request.user.is_premium:
        workouts = workouts.filter(is_premium=False)
    # Lekin bu filtered workouts results["workouts"] ga YOZILMAYDI!
    return Response(results)  # ← results["workouts"] hali premium filterlangan emas!
```

Ikkinchi query premium filterlaydi lekin natijani `results["workouts"]` ga saqlashni unutgan. Birinchi query natijasi qaytariladi — premium filterlanmagan holda.

---

### 🔴 #6 — `MealLogViewSet.summary` — noto'g'ri date format kiritilsa `HTTP 500`

**Fayl:** `nutrition/views.py`  
**Test:** `TEST61 Unhandled ValueError in summary() -> HTTP 500: time data 'bad-date' does not match format '%Y-%m-%d'`

**Muammo:**
```python
@action(detail=False, methods=['get'])
def summary(self, request):
    date_str = request.query_params.get('date')
    date = datetime.today().date() if not date_str else datetime.strptime(date_str, '%Y-%m-%d').date()
    # ↑ noto'g'ri format kelsa -> ValueError -> HTTP 500 Internal Server Error
```

`?date=2026-13-99` yoki `?date=abc` kabi noto'g'ri formatlar `try/except` bilan himoyalanmagan.

---

### 🔴 #7 — `UserChallengeViewSet.complete` — `end_date` validatsiyasiz saqlaydi

**Fayl:** `community/views.py`  
**Test:** `TEST65 UserChallenge.complete validates end_date format: False`

**Muammo:**
```python
def complete(self, request, pk=None):
    obj.end_date = request.data.get('end_date')  # ← string, datetime emas
    obj.save()
```

`end_date` `DateTimeField` ammo `request.data.get('end_date')` string formatida keladi. Django ba'zida qabul qilishi mumkin, lekin noto'g'ri format kelsa `ValidationError` yoki xato.

---

### 🔴 #8 — `UserWorkoutLogViewSet.complete` — `completed_at` validatsiyasiz

**Fayl:** `workouts/views.py`

**Muammo:**
```python
def complete(self, request, pk=None):
    log.completed_at = request.data.get('completed_at')  # string raw
    log.duration_seconds = request.data.get('duration_seconds')  # int check yo'q
    log.rating = request.data.get('rating')  # 1-5 range check yo'q
    log.save()
```

Serializer ishlatilmaydi. `completed_at` string, `rating` 1-5 dan tashqari qiymat qabul qilishi mumkin.

---

## 🟠 JIDDIY KAMCHILIKLAR

---

### 🟠 #9 — `UserRegisterSerializer.create` — `username=nickname` duplicate `IntegrityError`

**Fayl:** `users/serializers.py`  
**Test:** `TEST33 Save blocked: IntegrityError UNIQUE constraint failed: users_user.username`

**Muammo:**
```python
def create(self, validated_data):
    validated_data['username'] = validated_data['nickname']  # username = nickname
    user = User.objects.create_user(**validated_data)
```

Agar ikki foydalanuvchi bir xil `nickname` tanlasa, `username` ham bir xil bo'ladi va `UNIQUE constraint failed` xatosi kelib chiqadi. `serializer.is_valid()` bu holatni ushlamaydi — xato faqat `save()` da kelib chiqadi, client HTTP 500 ko'radi.

---

### 🟠 #10 — `ForumCommentSerializer.create` — mantiqsiz override

**Fayl:** `community/serializers.py`  
**Test:** `TEST36 BUG: pop then re-add same key`

**Muammo:**
```python
def create(self, validated_data):
    post_id = validated_data.pop('post_id')   # pop
    validated_data['post_id'] = post_id        # qayta qo'yish
    return super().create(validated_data)      # hech narsa o'zgarmadi
```

Bu override butunlay mantiqsiz — kalit o'chirib, qayta qo'yiladi. Hech qanday effekti yo'q. Bundan tashqari, `post_id` `validated_data` da bo'lmasligi mumkin (chunki `post` field `post_id` emas — serializer `post` fielddan foydalanadi) → `KeyError`.

---

### 🟠 #11 — `GeneratedMealPlanViewSet.perform_create` — noto'g'ri `related_name`

**Fayl:** `nutrition/views.py`  
**Test:** `TEST38 BUG: view uses "meal_preference" but related_name is "meal_plan_preference"`

**Muammo:**
```python
def perform_create(self, serializer):
    preference = getattr(user, 'meal_preference', None)  # ← NOTO'G'RI!
    # Model da related_name='meal_plan_preference'
```

`MealPlanPreference` modelida `related_name='meal_plan_preference'` belgilangan, lekin view `meal_preference` ni qidiradi. `getattr` `None` qaytaradi → preference hech qachon qo'llanilmaydi → meal plan avoidance filterlari ishlamaydi.

---

### 🟠 #12 — `ArticleViewSet` — draft maqolalar ham qaytariladi

**Fayl:** `content/views.py`  
**Test:** `TEST46 BUG: All articles including published_at=None returned` | `TEST69 Article has is_active: False`

**Muammo:**
```python
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()  # ← barcha maqolalar, draft ham!
```

`Article` modelida `published_at` nullable. `published_at=None` bo'lgan maqolalar (draft) ham API orqali qaytariladi. `is_active` field ham yo'q.

---

### 🟠 #13 — `UserWorkoutLog` — `workout` va `custom_routine` ikkalasi ham `None` bo'lishi mumkin

**Fayl:** `workouts/models.py`  
**Test:** `TEST48 BUG: No model-level validation`

**Muammo:**
```python
class UserWorkoutLog(models.Model):
    workout        = models.ForeignKey(Workout, null=True, blank=True, ...)
    custom_routine = models.ForeignKey(CustomRoutine, null=True, blank=True, ...)
    # ← hech qanday clean() yoki constraint yo'q
```

Qoidaga ko'ra kamida bittasi ko'rsatilishi kerak, lekin hech qanday model-level validatsiya yo'q. Ikkalasi ham `None` bo'lgan yozuv yaratish mumkin.

---

### 🟠 #14 — `SupportMessage.is_read` field API'da ko'rinmaydi

**Fayl:** `support/serializers.py`  
**Test:** `TEST67 SupportMessage.is_read in API fields: False`

**Muammo:**
```python
class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'message', 'is_from_user', 'created_at')
        # ↑ is_read yo'q! Admin o'qiganda user bilmaydi
```

`SupportMessage.is_read` model da mavjud, lekin serializer da ko'rsatilmagan. Foydalanuvchi o'z support xabarlarini o'qilgan-o'qilmaganligini bilmaydi.

---

### 🟠 #15 — `ForumPostViewSet` va `ForumCommentViewSet` — barcha post/comment qaytariladi (filter yo'q)

**Fayl:** `community/views.py`  
**Test:** `TEST62 ForumCommentViewSet returns all comments: True`

**Muammo:**
```python
class ForumPostViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return ForumPost.objects.all()       # hech qanday filter yo'q

class ForumCommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return ForumComment.objects.all()    # hech qanday filter yo'q
```

Postlar kategoriya bo'yicha filterlash imkoni serializer'da yo'q. Barcha postlar `GET /api/community/posts/` orqali qaytadi (pagination bor, lekin qidiruv filter yo'q). Eng muhimi — `ForumComment.objects.all()` barcha foydalanuvchilarning barcha commentlarini bir so'rovda qaytaradi.

---

### 🟠 #16 — `PostLike.toggle` — muvaffaqiyatli yaratishda `201` emas `200` qaytaradi

**Fayl:** `community/views.py`  
**Test:** `TEST64 PostLike toggle returns 201 on create: False`

**Muammo:**
```python
@action(detail=False, methods=['post'])
def toggle(self, request):
    like, created = PostLike.objects.get_or_create(...)
    if not created:
        like.delete()
        return Response({"liked": False})          # 200
    return Response({"liked": True})               # 200 ← 201 bo'lishi kerak
```

Yangi resurs yaratilganda `201 Created` qaytarishi kerak, lekin `200 OK` qaytaradi.

---

### 🟠 #17 — `WorkoutViewSet.recommended` — `get_queryset()` allaqachon `is_active=True` filter qiladi, lekin yana `filter(is_active=True)` chaqiriladi

**Fayl:** `workouts/views.py`

**Muammo:**
```python
def get_queryset(self):
    qs = Workout.objects.filter(is_active=True)   # ← avval
    ...

def recommended(self, request):
    qs = self.get_queryset().filter(is_active=True)   # ← qayta filter
```

Ikki marta `is_active=True` filter qilinadi — bu keraksiz, lekin xato emas.

---

### 🟠 #18 — `Article.author` — `User` FK emas, oddiy `CharField`

**Fayl:** `content/models.py`  
**Test:** `TEST29 Article.author is plain CharField: True`

**Muammo:**
```python
class Article(models.Model):
    author = models.CharField(max_length=250, null=True, blank=True)
    # ← User FK emas, plain text!
```

Maqola muallifi `User` bilan bog'liq emas. Kim yozganini tracking qilib bo'lmaydi. Foydalanuvchi o'chirilsa, maqola muallif ma'lumoti yo'qolmaydi (lekin bu ma'nosiz matn bo'ladi).

---

### 🟠 #19 — `notifications/translation.py` — bo'sh fayl

**Test:** `TEST66 notifications/translation.py empty: True`

**Muammo:**
`notifications/translation.py` fayli mavjud lekin butunlay bo'sh. Agar `Notification` modeli tarjima qilinishi rejalashtirilgan bo'lsa, bu fayl to'ldirilmagan. `NotificationAdmin` `TranslationAdmin` emas — izchilsizlik.

---

### 🟠 #20 — `UserWorkoutLogSerializer` — `user` field yo'q, `workout`/`custom_routine` write bo'lib qoladi

**Fayl:** `workouts/serializers.py`  
**Test:** `TEST47 user field in serializer: False`

**Muammo:**
```python
class UserWorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id', 'workout', 'workout_title', 'custom_routine',
            'started_at', 'completed_at', ...
        )
        read_only_fields = ('id', 'created_at')
```

- `user` field yo'q — client qaysi userga tegishli ekanini ko'rolmaydi
- `workout` va `custom_routine` FK fieldlari `read_only_fields` da emas, demak write qilinishi mumkin — boshqa userning ID'sini yozish mumkin

---

## 🟡 O'RTA DARAJALI KAMCHILIKLAR

---

### 🟡 #21 — `SECRET_KEY` kod ichida hardcoded va `django-insecure-` prefixli

**Fayl:** `config/settings.py`  
**Test:** `TEST39 SECRET_KEY insecure prefix: True`

```python
SECRET_KEY = 'django-insecure-yf-ql7%ak5f=%y^%be44#c)x+$vyehpy^2e3yhegvt!yr9celz'
```

Django `--deploy` tekshiruvida `security.W009` xatoligi: "SECRET_KEY is prefixed with 'django-insecure-'". Git'ga push qilinsa ochiq bo'lib qoladi.

---

### 🟡 #22 — `DEBUG=True`, `ALLOWED_HOSTS=['*']`, `CORS_ALLOW_ALL_ORIGINS=True`

**Fayl:** `config/settings.py`  
**Test:** `TEST40-42` barchasi tasdiqlandi

`manage.py check --deploy` quyidagi xatoliklarni beradi:
- `security.W018` — `DEBUG=True`
- `security.W004` — `SECURE_HSTS_SECONDS` o'rnatilmagan
- `security.W008` — `SECURE_SSL_REDIRECT=False`
- `security.W012` — `SESSION_COOKIE_SECURE` o'rnatilmagan
- `security.W016` — `CSRF_COOKIE_SECURE` o'rnatilmagan

---

### 🟡 #23 — `drf-spectacular` `check --deploy` da 44 ta warning

**Test:** `manage.py check --deploy` — `44 issues`

Ko'plab ViewSet larda `get_queryset()` `request.user` ga bog'liq bo'lgani uchun `drf_spectacular.W001` xatoliklari. Swagger schema to'liq generatsiya bo'lmaydi:
- `GlobalSearchView` schema'da yo'q (`W002`)
- `SupportReplyView`, `ChangePasswordView`, `DeleteAccountView`, `ForgotPasswordView`, `OnboardingView`, `ResetPasswordView` — schema'da yo'q
- `get_is_liked` type hint yo'q

---

### 🟡 #24 — `IsOwnerOrReadOnly` — `has_permission` implement qilinmagan

**Fayl:** `core/permissions.py`

```python
class IsOwnerOrReadOnly(BasePermission):
    # has_permission yo'q — list/create da permission tekshirilmaydi
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
```

`has_permission` yo'q bo'lgani uchun default `True` qaytaradi. `list` va `create` da object-level check ishlamaydi. Bu `ForumCommentViewSet` da xavfli — har bir authenticated user hamma commentni ko'ra oladi.

---

### 🟡 #25 — `IsPremiumUser` permission — hech qayerda ishlatilmaydi

**Fayl:** `core/permissions.py`  
**Test:** `TEST43 IsPremiumUser used in files: NOWHERE`

`IsPremiumUser` klass yaratilgan lekin birorta ham view da `permission_classes` ga qo'shilmagan. Premium content uchun `WorkoutViewSet.get_queryset` da `is_premium` filter bor, lekin bu permission klass emas — izchilsizlik.

---

### 🟡 #26 — `Article.published_at` nullable, lekin `Meta.ordering = ['-published_at']`

**Fayl:** `content/models.py`  
**Test:** `TEST20 published_at nullable: True`

```python
class Article(models.Model):
    published_at = models.DateTimeField(blank=True, null=True)  # nullable

    class Meta:
        ordering = ['-published_at']  # NULL qiymatlar tartiblashda muammo
```

SQLite da `NULL` oxirida, PostgreSQL da boshida joylashadi — DB ga ko'ra farqli tartib.

---

### 🟡 #27 — `UserWorkoutLog.complete` — `rating` 1-5 dan tashqari qiymat qabul qilishi mumkin

**Fayl:** `workouts/views.py`

```python
log.rating = request.data.get('rating')   # 0, 10, -1 qabul qilinadi
```

`UserWorkoutLog.rating = PositiveIntegerField(choices=[(i,i) for i in range(1,6)])` — choices belgilangan, lekin serializer ishlatilmagani uchun validatsiya o'tkazilmaydi.

---

### 🟡 #28 — `SupportChatConsumer` — rate limiting yo'q

**Fayl:** `support/consumers.py`  
**Test:** `TEST52 has rate limiting: False`

WebSocket `receive()` metodida hech qanday rate limiting yo'q. Foydalanuvchi sekundiga yuzlab xabar jo'natishi mumkin — spam va DB to'ldirishga olib keladi.

---

### 🟡 #29 — `AllowedHostsOriginValidator` bilan `ALLOWED_HOSTS=['*']` — WebSocket muammosi

**Fayl:** `config/asgi.py`, `config/settings.py`

```python
application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(...)
})
```

`AllowedHostsOriginValidator` ALLOWED_HOSTS ga qarab tekshiradi. `ALLOWED_HOSTS=['*']` production da ishlatilsa WebSocket barcha originlardan ochiq qoladi.

---

### 🟡 #30 — `PostLikeViewSet.toggle` — post_id `None` bo'lsa `400` qaytaradi, lekin post mavjud emasligi tekshirilmaydi

**Fayl:** `community/views.py`  
**Test:** `TEST60 Invalid UUID raises: ValidationError`

```python
def toggle(self, request):
    post_id = request.data.get('post')
    if not post_id:
        return Response({"detail": "post maydoni majburiy"}, status=400)
    like, created = PostLike.objects.get_or_create(user=request.user, post_id=post_id)
    # ↑ post mavjud emasligi tekshirilmaydi — IntegrityError chiqishi mumkin
```

`post_id` UUID formatida bo'lsa ham, tegishli `ForumPost` mavjud emasligi tekshirilmaydi.

---

### 🟡 #31 — `MealLog.logged_at` — timezone-naive datetime qabul qilinadi

**Fayl:** `nutrition/serializers.py`  
**Test:** `TEST49 MealLogSerializer naive datetime valid: True`

```python
logged_at = models.DateTimeField()
```

`USE_TZ = True` sozlangan holda timezone-naive datetime (masalan `"2026-09-17 10:00:00"`) serializer tomonidan qabul qilinadi. Bu `settings.TIME_ZONE='UTC'` da kichik muammo, lekin timezone-aware datetime tavsiya etiladi.

---

### 🟡 #32 — `WorkoutViewSet.get_permissions` — `permission_classes` to'g'ri ishlaydi, lekin `IsTrainerOrAdmin` `has_permission` yo'q holda `IsAuthenticated` bilan parallel

**Fayl:** `workouts/views.py`

```python
def get_permissions(self):
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
        return [IsAuthenticated(), IsTrainerOrAdmin()]
    return super().get_permissions()
```

Bu to'g'ri ishlaydi. Lekin `IsTrainerOrAdmin` da `has_object_permission` implement qilinmagan — object-level check trainer/admin uchun kuchsizroq.

---

### 🟡 #33 — `UserGoal.end_date < start_date` validatsiyasi yo'q

**Fayl:** `users/serializers.py`

`UserGoalSerializer` da `end_date > start_date` validatsiyasi yo'q. O'tmishdagi sana yoki end_date < start_date bo'lsa qabul qilinadi.

---

### 🟡 #34 — `Challenge.start_date`, `end_date` — o'tgan sana tekshirilmaydi

**Fayl:** `community/serializers.py`

`ChallengeSerializer` da `start_date` va `end_date` validatsiyasi yo'q. Admin o'tgan sana bilan challenge yaratishi mumkin.

---

### 🟡 #35 — `OnboardingView` — serializer ishlatmaydi, to'g'ridan-to'g'ri `request.data` ishlatadi

**Fayl:** `users/views.py`

```python
def post(self, request):
    user.fitness_level = data.get('fitness_level', user.fitness_level)
    user.primary_goal = data.get('primary_goal', user.primary_goal)
    user.save()  # ← serializer validation yo'q, choices tekshirilmaydi
```

`fitness_level = 'invalid_value'` kiritilsa ham qabul qilinadi va bazaga yoziladi.

---

### 🟡 #36 — `ExerciseLog` — `user` field yo'q, faqat `user_workout_log` FK orqali bilvosita

**Fayl:** `workouts/models.py`

`ExerciseLog` to'g'ridan-to'g'ri `user` field'i yo'q. `user_workout_log → user` orqali kirish mumkin. Admin da va API da user bo'yicha filter qilish qiyinroq.

---

## 🔵 TAVSIYALAR

---

### 🔵 #37 — SQLite production uchun mos emas

**Fayl:** `config/settings.py`

```python
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
```

Production da PostgreSQL ishlatish tavsiya etiladi. SQLite concurrent write operatsiyalari, full-text search, va katta hajmli ma'lumotlar uchun cheklovlarga ega.

---

### 🔵 #38 — JWT `ACCESS_TOKEN_LIFETIME = timedelta(days=1)` — juda uzun

**Fayl:** `config/settings.py`

```python
'ACCESS_TOKEN_LIFETIME': timedelta(days=1),    # 24 soat — juda uzun
'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
```

Access token odatda 15-60 daqiqa, refresh token esa 7-30 kun bo'lishi tavsiya etiladi. 24 soatlik access token tokenni o'g'irlash xavfini oshiradi.

---

### 🔵 #39 — Celery / task queue yo'q — notifikatsiyalar faqat sinxron

**Fayl:** barcha app

Notifikatsiya yaratish (`create_notification`) sinxron DB yozuvi. Email, push notification (FCM/APNs), yoki delayed notification uchun Celery/Django-Q kerak.

---

### 🔵 #40 — `IsPremiumUser` permission ishlatilmaydi

**Fayl:** `core/permissions.py`

Premium content uchun `WorkoutViewSet.get_queryset` da `is_premium` filter bor, lekin `IsPremiumUser` permission klass hech qayerda `permission_classes` ga qo'shilmagan. Izchillik yo'q.

---

### 🔵 #41 — `UserGoal` — progress foizi (`progress_percentage`) avtomatik hisoblanmaydi

**Fayl:** `users/models.py`  
**Test:** `TEST31 progress_percentage auto field: False`

`current_value` va `target_value` bor, lekin `progress_percentage = (current_value/target_value)*100` ni qaytaradigan `@property` yoki serializer metodi yo'q.

---

### 🔵 #42 — `ForumPost.likes_count` `@property` — N+1 query xavfi

**Fayl:** `community/models.py`

```python
@property
def comments_count(self):
    return self.comments.count()    # har post uchun alohida COUNT query

@property
def likes_count(self):
    return ... .count()             # har post uchun alohida COUNT query
```

`ForumPostSerializer` `ForumPost.objects.all()` ni serialize qilganda, har post uchun 2 ta qo'shimcha DB query kelib chiqadi — jami `2N+1` query. `annotate()` ishlatish kerak.

---

## Umumiy test natijalari jadvali

| # | Daraja | App | Fayl | Muammo | Test natijasi |
|---|---|---|---|---|---|
| 1 | 🔴 | users | `views.py` | `ForgotPasswordView` token HTTP'da ochiq, email yo'q | ✅ Tasdiqlandi |
| 2 | 🔴 | users | `views.py` | `DeleteAccountView` JWT token bekor qilinmaydi | ✅ Tasdiqlandi |
| 3 | 🔴 | workouts | `serializers.py` | `FavoriteWorkoutSerializer` `workout_id` yo'q → IntegrityError | ✅ Tasdiqlandi |
| 4 | 🔴 | nutrition | `serializers.py` | `FavoriteRecipeSerializer` `recipe_id` yo'q → IntegrityError | ✅ Tasdiqlandi |
| 5 | 🔴 | core | `views.py` | `GlobalSearchView` premium filter ishlamaydi, duplicate query | ✅ Tasdiqlandi |
| 6 | 🔴 | nutrition | `views.py` | `summary()` bad date format → HTTP 500 | ✅ Tasdiqlandi |
| 7 | 🔴 | community | `views.py` | `UserChallenge.complete` `end_date` validatsiyasiz | ✅ Tasdiqlandi |
| 8 | 🔴 | workouts | `views.py` | `UserWorkoutLog.complete` validatsiyasiz raw data | ✅ Tasdiqlandi |
| 9 | 🟠 | users | `serializers.py` | Duplicate nickname → `IntegrityError` (500) | ✅ Tasdiqlandi |
| 10 | 🟠 | community | `serializers.py` | `ForumCommentSerializer.create` mantiqsiz, KeyError xavfi | ✅ Tasdiqlandi |
| 11 | 🟠 | nutrition | `views.py` | `perform_create` noto'g'ri `related_name` (`meal_preference`) | ✅ Tasdiqlandi |
| 12 | 🟠 | content | `views.py` | Draft maqolalar ham qaytariladi | ✅ Tasdiqlandi |
| 13 | 🟠 | workouts | `models.py` | `UserWorkoutLog` ikkalasi `None` bo'lishi mumkin | ✅ Tasdiqlandi |
| 14 | 🟠 | support | `serializers.py` | `is_read` API da ko'rinmaydi | ✅ Tasdiqlandi |
| 15 | 🟠 | community | `views.py` | Barcha post/comment filterlarsiz qaytadi | ✅ Tasdiqlandi |
| 16 | 🟠 | community | `views.py` | `toggle` create da `201` emas `200` | ✅ Tasdiqlandi |
| 17 | 🟠 | workouts | `views.py` | `recommended` double `is_active=True` filter | ✅ Tasdiqlandi |
| 18 | 🟠 | content | `models.py` | `Article.author` FK emas, plain CharField | ✅ Tasdiqlandi |
| 19 | 🟠 | notifications | `translation.py` | Bo'sh fayl | ✅ Tasdiqlandi |
| 20 | 🟠 | workouts | `serializers.py` | `UserWorkoutLogSerializer` user yo'q, workout writable | ✅ Tasdiqlandi |
| 21 | 🟡 | config | `settings.py` | `SECRET_KEY` hardcoded, insecure prefix | ✅ Tasdiqlandi |
| 22 | 🟡 | config | `settings.py` | DEBUG, ALLOWED_HOSTS, CORS production uchun xavfli | ✅ Tasdiqlandi |
| 23 | 🟡 | barcha | `views.py` | `drf-spectacular` 44 ta warning | ✅ Tasdiqlandi |
| 24 | 🟡 | core | `permissions.py` | `IsOwnerOrReadOnly.has_permission` yo'q | — |
| 25 | 🟡 | core | `permissions.py` | `IsPremiumUser` hech qayerda ishlatilmaydi | ✅ Tasdiqlandi |
| 26 | 🟡 | content | `models.py` | `published_at=NULL` ordering muammosi | ✅ Tasdiqlandi |
| 27 | 🟡 | workouts | `views.py` | `rating` 1-5 validatsiyasiz qabul qilinadi | — |
| 28 | 🟡 | support | `consumers.py` | WebSocket rate limiting yo'q | ✅ Tasdiqlandi |
| 29 | 🟡 | config | `asgi.py` | `AllowedHostsOriginValidator` + `ALLOWED_HOSTS=['*']` | — |
| 30 | 🟡 | community | `views.py` | `toggle` post mavjudligi tekshirilmaydi | ✅ Tasdiqlandi |
| 31 | 🟡 | nutrition | `serializers.py` | `logged_at` timezone-naive qabul qilinadi | ✅ Tasdiqlandi |
| 32 | 🟡 | workouts | `views.py` | `IsTrainerOrAdmin` object-level check yo'q | — |
| 33 | 🟡 | users | `serializers.py` | `end_date < start_date` validatsiyasi yo'q | — |
| 34 | 🟡 | community | `serializers.py` | Challenge o'tgan sana bilan yaratilishi mumkin | — |
| 35 | 🟡 | users | `views.py` | `OnboardingView` serializer ishlatmaydi, choices tekshirilmaydi | — |
| 36 | 🟡 | workouts | `models.py` | `ExerciseLog` to'g'ridan-to'g'ri `user` FK yo'q | — |
| 37 | 🔵 | config | `settings.py` | SQLite production uchun mos emas | — |
| 38 | 🔵 | config | `settings.py` | JWT access token 24 soat — juda uzun | — |
| 39 | 🔵 | barcha | — | Celery/task queue yo'q | — |
| 40 | 🔵 | core | `permissions.py` | `IsPremiumUser` ishlatilmaydi | ✅ Tasdiqlandi |
| 41 | 🔵 | users | `models.py` | `UserGoal` progress foizi yo'q | ✅ Tasdiqlandi |
| 42 | 🔵 | community | `models.py` | `ForumPost` N+1 query xavfi | — |

---

## Xulosa

| Daraja | Soni |
|---|---|
| 🔴 Kritik | **8 ta** |
| 🟠 Jiddiy | **12 ta** |
| 🟡 O'rta | **16 ta** |
| 🔵 Tavsiya | **6 ta** |
| **Jami** | **42 ta** |

**Eng muhim:** `ForgotPasswordView` xavfsizlik kamchiligi (#1), `FavoriteWorkoutSerializer` va `FavoriteRecipeSerializer` IntegrityError (#3, #4), va `GlobalSearchView` premium filter (#5) ni birinchi navbatda tuzatish tavsiya etiladi.
