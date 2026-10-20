from django.utils import translation


def set_language_from_user(request):
    """
    JWT auth dan keyin chaqiriladi.
    ?lang= allaqachon qo‘yilgan bo‘lsa — o‘zgartirmaydi.
    """
    if getattr(request, 'LANGUAGE_CODE', None) in ('uz', 'en', 'ru'):
        return

    if request.user.is_authenticated:
        try:
            lang = request.user.settings.language
            if lang in ('uz', 'en', 'ru'):
                translation.activate(lang)
                request.LANGUAGE_CODE = lang
        except Exception:
            pass