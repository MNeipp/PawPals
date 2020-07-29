from django.shortcuts import render, redirect, reverse
import json
import petpy
from datetime import datetime, date, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from user_app.models import User

pf = petpy.Petfinder(key='cET5qlEkj0mMIFKIFkigu7y5mOk6hBeiYKLzylnaHvleQan7y6', secret='gq5c8x0leW4pOs65cXuXu3KV6kiCCPvIxLl4K4sM')
today = datetime.today()


# Create your views here.


def index(request):
    if 'user_id' in request.session:
        context = {
            'breeds': pf.breeds(types=['dog']),
            'logged_user': User.objects.get(id=request.session['user_id'])
        }
        return render(request, 'adopt/index.html', context)
    else:
        context={
            'breed': pf.breeds(types=['dog']),
        }
        return render(request, 'adopt/index.html', context)


def search(request):
    if request.method == "POST":
        if request.POST['age'] == '':
            age = None
        else:
            age = request.POST['age']
        if request.POST['size'] == '':
            size = None
        else:
            size = request.POST['size']
        if request.POST['location'] == '':
            location = None
        else:
            location = request.POST['location']
        if request.POST['distance'] == '':
            distance = None
        else:
            distance = request.POST['distance']
        if request.POST['breed'] == '':
            breed = None
        else:
            breed = request.POST['breed']
        if 'gender' not in request.POST:
            gender = None
        elif request.POST['gender'] == '':
            gender=None
        else:
            gender = request.POST['gender']
        if 'gets_along' not in request.POST:
            good_with_children = None
            good_with_dogs = None
            good_with_cats = None
        elif request.POST['gets_along'] == '':
            good_with_children = None
            good_with_dogs = None
            good_with_cats = None
        elif request.POST['gets_along'] == 'kids':
            good_with_children = True
            good_with_dogs = None
            good_with_cats = None
        elif request.POST['gets_along'] == 'dogs':
            good_with_children = None
            good_with_dogs = True
            good_with_cats = None
        elif request.POST['gets_along'] == 'cats':
            good_with_children = None
            good_with_dogs = None
            good_with_cats = True
        if 'after_date' == '':
            after_date = None
        else:
            after_date = today - timedelta(days=int(request.POST['after_date']))
        
        dogs = pf.animals(
          animal_type='dog',
          status='adoptable',
          location=location,
          distance=distance,
          size=size,
          age=age,
          breed=breed,
          gender=gender,
          pages=None,
          good_with_children=good_with_children,
          good_with_cats=good_with_cats,
          good_with_dogs=good_with_dogs,
          after_date = after_date
        )

        context = {
            'dogs': dogs['animals'],
            'breeds': pf.breeds(types=['dog'])
        }
        return render(request, 'adopt/search.html', context)

    else:
        context = {
            'breeds': pf.breeds(types=['dog'])
        }
        return render(request, 'adopt/search.html', context)

def pet_detail(request, dog_id):
    dog = pf.animals(animal_id=dog_id)
    context = {
        "dog": dog,
        "organization": pf.organizations(organization_id=dog['animals']['organization_id'])['organizations'],
        "date": datetime.strptime(dog['animals']['published_at'], '%Y-%m-%dT%H:%M:%S%z').date()
    }
    return render(request, 'adopt/pet_detail.html', context)


def shelters(request):
    if 'name' in request.GET and request.GET['name'] !='':
        name = request.GET['name']
        context={
            "organizations": pf.organizations(pages=None, name=name)['organizations']
        }
        return render(request,'adopt/shelters.html', context)
    elif 'city' in request.GET and 'state' in request.GET:
        location = f"{request.GET['city']}, {request.GET['state']}"
        if 'zip' in request.GET and request.GET['zip'] != '':
            location = request.GET['zip']
        if 'distance' in request.GET:
            distance = request.GET['distance']
        else: 
            distance = 5
        if 'sort' in request.GET:
            sort = request.GET['sort']
        else:
            sort = None
        organizations = Paginator(pf.organizations(location=location, distance=distance, pages=None, sort=sort)['organizations'],5)
        page = request.GET.get('page', 1)
        try:
            organizations = organizations.page(page)
        except PageNotAnInteger:
            organizations = organizations.page(1)
        except EmptyPage:
            organizations = organizations.page(organizations.num_pages)
        path = ''
        path += "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in request.GET.items() if not key=='page' ])
        context={
            "organizations": organizations,
            "closest": pf.organizations(location=location, distance=distance, pages=None, sort='distance')['organizations'][0],
            "path":path
        }           
        return render(request,'adopt/shelters.html', context)
    else:
        return render(request, 'adopt/shelters.html')


def shelter_detail(request, shelter_id):
    organization = pf.organizations(organization_id=shelter_id)
    context = {
        "organization": organization['organizations'],
        "dogs": pf.animals(organization_id=shelter_id, pages=None, animal_type='dog')['animals'],
        "breeds": pf.breeds(types=['dog']),
    }
    return render(request, 'adopt/shelter_detail.html', context)


def about(request):
    # quick bio page
    return render(request, 'adopt/about.html')
