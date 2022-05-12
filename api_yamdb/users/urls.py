from django.urls import path, include
from users.views import register, obtain_token_view, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/', obtain_token_view),
    path('auth/signup/', register)
]

urlpatterns += router.urls
