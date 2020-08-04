from django.shortcuts import render, reverse, redirect, HttpResponseRedirect
from django.contrib import messages
from .models import User
import bcrypt, petpy
from adopt_app.models import Pet

pf = petpy.Petfinder(key='cET5qlEkj0mMIFKIFkigu7y5mOk6hBeiYKLzylnaHvleQan7y6', secret='gq5c8x0leW4pOs65cXuXu3KV6kiCCPvIxLl4K4sM')


# Create your views here.


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        if len(request.POST['email']) < 5:
            messages.error(request, "Please enter a valid e-mail", extra_tags="email")
            return redirect(reverse('login'))
        user = User.objects.filter(email__iexact=request.POST['email'])
        request.session['email'] = request.POST['email']
        if user:
            logged_user = user[0]
            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                request.session['user_id'] = logged_user.id
                next = request.POST.get('next', '/')
                if next == '':
                    return redirect(reverse('search'))
                return HttpResponseRedirect(next)
            else:
                messages.error(request, "Incorrect password or e-mail", extra_tags="password")
                return redirect(reverse('login'))
        else:
            messages.error(request, "Incorrect password or e-mail", extra_tags="email")
            return redirect(reverse('login'))


def register(request):
    if request.method == "GET":
        return render(request, "register.html")
    elif request.method == "POST":
        errors = User.objects.basic_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return redirect(reverse('register'))
        else:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password = request.POST['password']
            pswd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=pswd_hash
                )
            if "user_id" not in request.session:
                request.session['user_id'] = user.id
            return redirect(reverse("home"))


def logout(request):
    request.session.flush()
    return redirect(reverse("home"))


def user_profile(request):
    if 'user_id' not in request.session:
        return reverse('login')
    else:
        context = {
            'logged_user': User.objects.get(id=request.session['user_id'])
        }
        return render(request, "user_profile.html", context)


def update_profile(request):
    if request.method == "GET":
        return redirect(reverse('index'))
    errors = User.objects.info_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    logged_user = User.objects.get(id=request.session['user_id'])
    logged_user.first_name = request.POST['first_name']
    logged_user.last_name = request.POST['last_name']
    logged_user.email = request.POST['email']
    if 'profile_picture' in request.FILES:
        logged_user.image = request.FILES['profile_picture']
    logged_user.save()
    if request.POST['current_password']:
        if bcrypt.checkpw(request.POST['current_password'].encode(), logged_user.password.encode()):
            if len(request.POST['new_password']) < 8:
                messages.error(request, "Password must be at least 8 characters long", extra_tags="confirm")
                return redirect(reverse('user_profile'))
            elif request.POST['new_password'] != request.POST['confirm_password']:
                messages.error(request, "Passwords don't match", extra_tags="confirm")
                return redirect(reverse('user_profile'))
            else:
                password = request.POST['new_password']
                pswd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                logged_user.password = pswd_hash
                logged_user.save()
                return redirect(reverse('user_profile'))
        else:
            messages.error(request, "Incorrect password", extra_tags="password")
            return redirect(reverse('user_profile'))

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def update_password(request):
    if request.method == "GET":
        return redirect(reverse('index'))
    logged_user = User.objects.get(id=request.session['user_id'])
    if bcrypt.checkpw(request.POST['current_password'].encode(), logged_user.password.encode()):
        if len(request.POST['new_password']) < 8:
            messages.error(request, "Password must be at least 8 characters long", extra_tags="confirm")
            return redirect(reverse('user_profile'))
        elif request.POST['new_password'] != request.POST['confirm_password']:
            messages.error(request, "Passwords don't match", extra_tags="confirm")
            return redirect(reverse('user_profile'))
        else:
            password = request.POST['new_password']
            pswd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            logged_user.password = pswd_hash
            logged_user.save()
            return redirect(reverse('user_profile'))
    else:
        messages.error(request, "Incorrect password", extra_tags="password")
        return redirect(reverse('user_profile'))


def favorites(request):
    # return user's favorites
    if 'user_id' not in request.session:
        return redirect(reverse('home'))
    logged_user = User.objects.get(id=request.session['user_id'])
    pets = Pet.objects.filter(faved_by__id=request.session['user_id'])
    fave_ids = [pet.petfinder_id for pet in pets]
    faves = []
    adoption_count = 0
    for pet in pets:
        try:
            faves.append(pf.animals(animal_id=pet.petfinder_id)['animals'])
        except:
            # Catches pets no longer available and removes them from the user's favorites
            adoption_count += 1
            this_pet = Pet.objects.get(petfinder_id__iexact=pet.petfinder_id)
            logged_user.has_faves.remove(this_pet)
            this_pet.delete()
    context = {
        'logged_user': logged_user,
        'faves': faves,
        'adoption_count': adoption_count,
        'fave_ids': fave_ids
    }

    return render(request, 'favorites.html', context)
