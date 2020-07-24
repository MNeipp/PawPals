from django.shortcuts import render


# Create your views here.


def index(request):
    return render(request, 'adopt/index.html')


def search(request):
    return render(request, 'adopt/search.html')


def search_query(request):
    pass


def pet_detail(request, id):
    return render(request, 'adopt/pet_detail.html')


def shelters(request):
    pass


def shelter_detail(request, id):
    return render(request, 'adopt/shelter_detail.html')
