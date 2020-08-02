from django.shortcuts import render, redirect, reverse
import json, petpy
from datetime import datetime, date, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from user_app.models import User
from .models import Pet
from django.contrib import messages

pf = petpy.Petfinder(key='cET5qlEkj0mMIFKIFkigu7y5mOk6hBeiYKLzylnaHvleQan7y6', secret='gq5c8x0leW4pOs65cXuXu3KV6kiCCPvIxLl4K4sM')
today = datetime.today()


def index(request):
    context = {
        'breed': pf.breeds(types=['dog']),
        }
    if 'user_id' in request.session:
        context.update({'logged_user': User.objects.get(id=request.session['user_id'])})  
    return render(request, 'adopt/index.html', context)


def search(request):
    if 'search' in request.GET:
        if request.GET['age'] == '':
            age = None
        else:
            age = request.GET['age']
        if request.GET['size'] == '':
            size = None
        else:
            size = request.GET['size']
        if request.GET['location'] == '':
            location = None
        else:
            location = request.GET['location']
        if request.GET['distance'] == '':
            distance = None
        else:
            distance = request.GET['distance']
        if request.GET['breed'] == '':
            breed = None
        else:
            breed = request.GET['breed']
        if 'gender' not in request.GET:
            gender = None
        elif request.GET['gender'] == '':
            gender = None
        else:
            gender = request.GET['gender']
        if 'gets_along' not in request.GET:
            good_with_children = None
            good_with_dogs = None
            good_with_cats = None
        elif request.GET['gets_along'] == '':
            good_with_children = None
            good_with_dogs = None
            good_with_cats = None
        elif request.GET['gets_along'] == 'kids':
            good_with_children = True
            good_with_dogs = None
            good_with_cats = None
        elif request.GET['gets_along'] == 'dogs':
            good_with_children = None
            good_with_dogs = True
            good_with_cats = None
        elif request.GET['gets_along'] == 'cats':
            good_with_children = None
            good_with_dogs = None
            good_with_cats = True
        if 'after_date' not in request.GET or request.GET['after_date'] == 'any':
            after_date = None
        else:
            after_date = today - timedelta(days=int(request.GET['after_date']))
        if 'sort' in request.GET:
            sort = request.GET['sort']
        else:
            sort = None
    
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
          after_date=after_date,
          sort=sort
        )
        dog_count = len(dogs['animals'])
        dogs = Paginator(dogs['animals'], 9)
        page = request.GET.get('page', 1)
        try:
            dogs = dogs.page(page)
        except PageNotAnInteger:
            dogs = dogs.page(1)
        except EmptyPage:
            dogs = dogs.page(dogs.num_pages)
        path = ''
        path += "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in request.GET.items() if not key=='page' and not key=='sort'])
        context = {
            'dogs': dogs,
            'breeds': pf.breeds(types=['dog']),
            'path': path,
            'dog_count': dog_count,
        }
        if 'user_id' in request.session:
            context.update({'logged_user': User.objects.get(id=request.session['user_id'])})
            pets = Pet.objects.filter(faved_by__id=request.session['user_id'])
            context.update({'faves': [pet.petfinder_id for pet in pets]})
        return render(request, 'adopt/search.html', context)

    else:
        context = {
            'breeds': pf.breeds(types=['dog']),
        }
        if 'user_id' in request.session:
            context.update({'logged_user': User.objects.get(id=request.session['user_id'])})  
        return render(request, 'adopt/search.html', context)

def pet_detail(request, dog_id):
    dog = pf.animals(animal_id=dog_id)
    context = {
        "dog": dog,
        "organization": pf.organizations(organization_id=dog['animals']['organization_id'])['organizations'],
        "date": datetime.strptime(dog['animals']['published_at'], '%Y-%m-%dT%H:%M:%S%z').date()
    }
    if 'user_id' in request.session:
        context.update({'logged_user': User.objects.get(id=request.session['user_id'])})  
        pets = Pet.objects.filter(faved_by__id=request.session['user_id'])
        context.update({'faves': [pet.petfinder_id for pet in pets]})
    return render(request, 'adopt/pet_detail.html', context)

def shelters(request):
    if 'name' in request.GET and request.GET['name'] !='':
        name = request.GET['name']
        messages.success(request, f"Results for {name}")
        context = {
            "organizations": pf.organizations(pages=None, name=name)['organizations']
        }
        if 'user_id' in request.session:
            context.update({'logged_user': User.objects.get(id=request.session['user_id'])})
        return render(request, 'adopt/shelters.html', context)

    elif 'city' in request.GET and 'state' in request.GET:
        if request.GET['city'] == '' and request.GET['state'] == '' and request.GET['zip'] == '':
            messages.error(request, "You must enter a City and State or Zip Code or Name", extra_tags='location')
            context = {}
            if 'user_id' in request.session:
                context.update({'logged_user': User.objects.get(id=request.session['user_id'])})  
            return render(request, 'adopt/shelters.html', context)
        else:
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
        path += "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in request.GET.items() if not key=='page'])
        
        messages.success(request, f"Results for {location}", extra_tags='success')
        context = {
            "organizations": organizations,
            "closest": pf.organizations(location=location, distance=distance, pages=None, sort='distance')['organizations'][0],
            "path": path
        }
        if 'user_id' in request.session:
            context.update({'logged_user': User.objects.get(id=request.session['user_id'])})       
        return render(request, 'adopt/shelters.html', context)
    else:
        if 'user_id' in request.session:
            context = {
                'logged_user': User.objects.get(id=request.session['user_id'])
            }
            return render(request, 'adopt/shelters.html', context)
        return render(request, 'adopt/shelters.html')

def shelters_ajax(request):
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
    path += "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in request.GET.items() if not key=='page'])
    context = {
        "organizations": organizations,
        "closest": pf.organizations(location=location, distance=distance, pages=None, sort='distance')['organizations'][0],
        "path": path
    }    
    return render(request, 'snippets/shelters_snippet.html', context)


def shelter_detail(request, shelter_id):
    organization = pf.organizations(organization_id=shelter_id)
    if 'sort' in request.GET:
        sort = request.GET['sort']
    else:
        sort = None
    context = {
        "organization": organization['organizations'],
        "dogs": pf.animals(organization_id=shelter_id, pages=None, animal_type='dog', sort=sort)['animals'],
        "breeds": pf.breeds(types=['dog']),
    }
    if 'user_id' in request.session:
        context.update({'logged_user': User.objects.get(id=request.session['user_id'])})    
    return render(request, 'adopt/shelter_detail.html', context)


def about(request):
    # quick bio page
    context = {
    }
    if 'user_id' in request.session:
        context.update({'logged_user': User.objects.get(id=request.session['user_id'])})  
    return render(request, 'adopt/about.html', context)


def add_favorite(request, dog_id):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in to add to your favorites!")
        return redirect('pet_detail', dog_id)
    # check if pet is already in DB:
    pet = Pet.objects.filter(petfinder_id__iexact=dog_id)

    # if not in DB, create new Pet, storing Pet's petfinder_id in DB:
    if len(pet) < 1:
        new_pet = Pet.objects.create(petfinder_id=dog_id)
        this_pet = Pet.objects.get(id=new_pet.id)

    else:
        this_pet = Pet.objects.get(id=pet[0].id)

    # create favorites relationship
    logged_user = User.objects.get(id=request.session['user_id'])
    logged_user.has_faves.add(this_pet)
    messages.success(request, "Successfully added to your favorites!")

    return redirect('pet_detail', dog_id)

def remove_favorite(request, dog_id):
    # get the pet
    this_pet = Pet.objects.get(petfinder_id__iexact=dog_id)
    logged_user = User.objects.get(id=request.session['user_id'])
    logged_user.has_faves.remove(this_pet)
    messages.success(request, "Successfully removed from your favorites!")
    return redirect('pet_detail', dog_id)
