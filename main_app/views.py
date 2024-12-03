from django.shortcuts import redirect, render

# Import the Cat and Toy models
from .models import Cat, Toy

# Import View classes to 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView

# Import the authentication views
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
# Import the login_required decorator on view functions
from django.contrib.auth.decorators import login_required
# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin

# Import the FeedingForm
from .forms import FeedingForm

# Create your views here.

# Import HttpResponse to send text-based responses
from django.http import HttpResponse

# class Cat:
#     def __init__(self, name, breed, description, age):
#         self.name = name
#         self.breed = breed
#         self.description = description
#         self.age = age

# # Create a list of Cat instances
# cats = [
#     Cat('Lolo', 'tabby', 'Kinda rude.', 3),
#     Cat('Sachi', 'tortoiseshell', 'Looks like a turtle.', 0),
#     Cat('Fancy', 'bombay', 'Happy fluff ball.', 4),
#     Cat('Bonk', 'selkirk rex', 'Meows loudly.', 6)
# ]


# Regular views

# Define the home view function
# def home(request):
#     # Send a simple HTML response
#     return render(request, 'home.html')

# Use the LoginView to handle user authentication in the home view
class Home(LoginView):
    template_name = 'home.html'

def about(request):
    return render(request, 'about.html')

# def cat_index(request):
#     # # Render the cats/index.html template with the cats data
#     # return render(request, 'cats/index.html', {'cats': cats})
#     cats = Cat.objects.all()  # look familiar?
#     return render(request, 'cats/index.html', {'cats': cats})

@login_required
def cat_index(request):
    cats = Cat.objects.filter(user=request.user)
    # You could also retrieve the logged in user's cats like this
    # cats = request.user.cat_set.all()
    return render(request, 'cats/index.html', { 'cats': cats })

@login_required
def cat_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    # toys = Toy.objects.all()
    toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list('id')) # get all toys that the cat doesn't have
    # instantiate FeedingForm to be rendered in the template
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', {
        # include the cat and feeding_form in the context
        'cat': cat, 
        'feeding_form': feeding_form,
        # Add the toys to be displayed on the cat detail page
        'toys': toys_cat_doesnt_have
    })

@login_required
def add_feeding(request, cat_id):
        # create a ModelForm instance using the data in request.POST
    form = FeedingForm(request.POST)
    # check if the form is valid aka checking if it follows the rules we set in the model
    if form.is_valid():
        # don't save the form to the db until it
        # has the cat_id assigned
        new_feeding = form.save(commit=False) # create a new feeding instance but don't save it to the db 
        # assign the cat_id to the new_feeding instance
        new_feeding.cat_id = cat_id
        # save the new_feeding instance to the db
        new_feeding.save()
    return redirect('cat-detail', cat_id=cat_id)

@login_required
def associate_toy(request, cat_id, toy_id):
    # Note that you can pass a toy's id instead of the whole object
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('cat-detail', cat_id=cat_id)

@login_required
def remove_toy(request, cat_id, toy_id):
    # Look up the cat
    cat = Cat.objects.get(id=cat_id)
    # Look up the toy
    toy = Toy.objects.get(id=toy_id)
    # Remove the toy from the cat
    cat.toys.remove(toy) # remove the toy from the cat's toys providing the toy object as an argument
    cat.save()
    return redirect('cat-detail', cat_id=cat.id)

# CBVs (Class Based Views)
class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    # template_name = 'books/index.html'
    # fields = '__all__'
    fields = ['name', 'breed', 'description', 'age']
    success_url = '/cats/'
    
    # This inherited method is called when a
    # valid cat form is being submitted
    # just a complicated if user is logged in
    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        # attach the user from the request to the user that will be inside the form data
        form.instance.user = self.request.user  # form.instance is the cat
        
        # Let the CreateView do its job as usual
        # then we want the the form validation to that already exists on the original CreateView to continue to do its own thing
        return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'

class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = '__all__'

class ToyList(LoginRequiredMixin, ListView):
    model = Toy

class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy

class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']

class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'


def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in
            login(request, user)
            return redirect('cat-index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)
    # Same as: 
    # return render(
    #     request, 
    #     'signup.html',
    #     {'form': form, 'error_message': error_message}
    # )