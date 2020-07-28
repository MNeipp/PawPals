from django.shortcuts import render, redirect, reverse
import json
from django.views.decorators.csrf import csrf_exempt
import petpy
from datetime import datetime

pf = petpy.Petfinder(key='cET5qlEkj0mMIFKIFkigu7y5mOk6hBeiYKLzylnaHvleQan7y6', secret='gq5c8x0leW4pOs65cXuXu3KV6kiCCPvIxLl4K4sM')


# Create your views here.


def index(request):
    context ={
        'breeds':pf.breeds(types=['dog'])
    }
    return render(request, 'adopt/index.html', context)



def search(request):
    if request.method == "POST":
        if request.POST['age'] == '' and request.POST['size'] == '':
            dogs = pf.animals(animal_type='dog', status = 'adoptable', location=request.POST['location'], distance=request.POST['distance'], breed=request.POST['breed'], pages=None)
        elif request.POST['age'] == '':
            dogs = pf.animals(animal_type='dog', status = 'adoptable', location=request.POST['location'], distance=request.POST['distance'], size=request.POST['size'], breed=request.POST['breed'], pages=None)
        elif request.POST['size'] == '':
             dogs = pf.animals(animal_type='dog', status = 'adoptable', location=request.POST['location'], distance=request.POST['distance'], age=request.POST['age'], breed=request.POST['breed'], pages=None)
        else:
            dogs = pf.animals(animal_type='dog', status = 'adoptable', location=request.POST['location'], distance=request.POST['distance'], size=request.POST['size'], age=request.POST['age'], breed=request.POST['breed'], pages=None)
        context = {
            'dogs': dogs['animals'],
            'breeds':pf.breeds(types=['dog'])
        }
        return render(request, 'adopt/search.html',context)
    else:
        context ={
            'breeds':pf.breeds(types=['dog'])
        }
        return render(request, 'adopt/search.html', context)


def search_query(request):
    print(request.POST)
    return redirect(reverse('search'))


def pet_detail(request, dog_id):
    dog = pf.animals(animal_id=dog_id)
    context={
        "dog": dog,
        "organization": pf.organizations(organization_id=dog['animals']['organization_id'])['organizations'],
        "date": datetime.strptime(dog['animals']['published_at'], '%Y-%m-%dT%H:%M:%S%z').date()
    }

    return render(request, 'adopt/pet_detail.html', context)


def shelters(request):
    return render(request, 'adopt/shelters.html')


def shelter_detail(request, shelter_id):
    organization = pf.organizations(organization_id = shelter_id)
    context={
        "organization": organization['organizations'],
        "dogs": pf.animals(organization_id=shelter_id,pages=None, animal_type='dog')['animals'],
        'breeds':pf.breeds(types=['dog']),
    }
    return render(request, 'adopt/shelter_detail.html', context)


def about(request):
    # quick bio page
    return render(request, 'adopt/about.html')
