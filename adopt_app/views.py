from django.shortcuts import render, redirect
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.


def index(request):
    return render(request, 'adopt/index.html')


@csrf_exempt
def search(request):
    # if request.method == "POST":
    #     dogs = request.body.decode("utf-8")
    #     dogs = json.loads(dogs)
    #     context = {
    #         "dogs": dogs
    #     }
    #     return render(request, 'adopt/search.html', context)
    # else:
    return render(request, 'adopt/search.html')


def search_query(request):

    return redirect('adopt/search.html)')


def pet_detail(request, id):
    return render(request, 'adopt/pet_detail.html')


def shelters(request):
    return render(request, 'adopt/shelters.html')


def shelter_detail(request, id):
    return render(request, 'adopt/shelter_detail.html')


def about(request):
    # quick bio page
    return render(request, 'adopt/about.html')
