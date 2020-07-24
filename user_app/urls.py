from django.urls import path
from . import views as user_views


urlpatterns = [
    path('login', user_views.login, name="login"),
    path('login/new', user_views.register, name="register"),
    path('logout', user_views.logout, name="logout"),
    path('profile', user_views.user_profile, name="user_profile"),
    path('profile/update', user_views.update_profile, name="update_user_profile"),
    path('profile/update_password', user_views.update_password, name="update_password"),
]