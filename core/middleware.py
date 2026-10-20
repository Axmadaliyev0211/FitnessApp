from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class UserLanguageMiddleware(MiddlewareMixin):
    """
    Til prioriteti (yuqoridan pastga):
      1. ?lang= query param  — eng yuqori
      2. Accept-Language header — (LocaleMiddleware tomonidan)
      3. UserSettings.language — foydalanuvchi saqlagan til
         (faqat Accept-Language KELMAGAN bo'lsa ishlatiladi)
    """

    def process_request(self, request):
        # 1. ?lang= query param — eng yuqori prioritet
        lang = request.GET.get('lang')
        if lang in ('uz', 'en', 'ru'):
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
            return

        # 2. Accept-Language header bor bo'lsa — LocaleMiddleware ishlasin
        #    Bu middleware Accept-Language ni OVERRIDE QILMAYDI
        accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept_lang:
            # LocaleMiddleware ishlagandan keyin til o'rnatiladi — bu yerda
            # faqat user settings ni process_response da qo'llash mumkin
            return

        # 3. Accept-Language yo'q + ?lang= yo'q → UserSettings.language ishlatamiz
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            try:
                from rest_framework_simplejwt.authentication import JWTAuthentication
                jwt_auth = JWTAuthentication()
                validated = jwt_auth.get_validated_token(
                    jwt_auth.get_raw_token(
                        jwt_auth.get_header(request)
                    )
                )
                user = jwt_auth.get_user(validated)
                if user and user.is_authenticated:
                    user_lang = getattr(getattr(user, 'settings', None), 'language', None)
                    if user_lang in ('uz', 'en', 'ru'):
                        translation.activate(user_lang)
                        request.LANGUAGE_CODE = user_lang
            except Exception:
                pass
