from django.urls import path
from .views import list_modules, professor_ratings, rate_professor, professor_module_rating_view, register_view, login_view, logout_view
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/modules/', list_modules, name='list_modules'),
    path("api/professor-ratings/", professor_ratings, name="professor_ratings"),
    path('api/professors/<str:professor_id>/modules/<str:module_id>/rating/', professor_module_rating_view.as_view(), name='professor-module-rating'),
    path('api/ratings/', rate_professor, name='rate_professor'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]


