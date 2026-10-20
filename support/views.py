from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import FAQ, SupportMessage
from .serializers import FAQSerializer, SupportMessageSerializer, SupportReplySerializer
from core.permissions import IsOwner
from core.language import set_language_from_user


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)


class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return SupportMessage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_from_user=True)



class SupportReplyView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = SupportReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        message_text = serializer.validated_data['message']

        msg = SupportMessage.objects.create(
            user_id=user_id,
            message=message_text,
            is_from_user=False
        )

        # WebSocket orqali real-time javob — agar channels mavjud bo'lsa
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                async_to_sync(channel_layer.group_send)(
                    f"support_{user_id}",
                    {
                        "type": "chat_message",
                        "message": {
                            "id": str(msg.id),
                            "message": msg.message,
                            "is_from_user": False,
                            "created_at": msg.created_at.isoformat()
                        }
                    }
                )
        except Exception:
            # PythonAnywhere yoki channels yo'q — WebSocket ishlamaydi,
            # lekin REST API javob normal qaytadi
            pass

        return Response({
            "detail": "Javob yuborildi",
            "message": {
                "id": str(msg.id),
                "message": msg.message,
                "is_from_user": False,
                "created_at": msg.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)