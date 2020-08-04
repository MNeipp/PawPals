from django.urls import path
from . import views as adopt_views

urlpatterns = [
    path('', adopt_views.index, name="home"),
    path('search/', adopt_views.search, name="search"),
    path('pets/<int:dog_id>', adopt_views.pet_detail, name="pet_detail"),
    path('pets/add_favorite/<int:dog_id>', adopt_views.add_favorite, name="add_favorite"),
    path('pets/remove_favorite/<int:dog_id>', adopt_views.remove_favorite, name="remove_favorite"),
    path('shelters', adopt_views.shelters, name="shelters"),
    path('shelters-ajax', adopt_views.shelters_ajax, name="shelters_ajax"),
    path('shelters/<str:shelter_id>', adopt_views.shelter_detail, name="shelter_detail"),
    path('about/', adopt_views.about, name="about")
]
