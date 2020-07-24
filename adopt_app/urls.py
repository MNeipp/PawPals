from django.urls import path
from . import views as adopt_views


urlpatterns = [
    path('adopt', adopt_views.index, name="home"),
    path('search', adopt_views.search, name="search"),
    path('search/query', adopt_views.search_query, name="query"),
    path('pet_detail/<int:id>', adopt_views.pet_detail, name="pet_detail"),
    path('shelters', adopt_views.shelter, name="shelters"),
    path('shetlers/<int:id>', adopt_views.shelter_detail, name="shelter_detail"),
]