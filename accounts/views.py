from django.shortcuts import redirect, render
from .forms import UserForm
from .models import User
from django.contrib import messages

# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        #this form gets automatically be validated using the is_valid() function that we have here
        # it is responsible for giving us all these kinds of field errors.
        if form.is_valid():
            # ##create the user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False) # Create an instance of the model from the form but don't save it yet to the database
            # user.role = User.CUSTOMER
            # user.set_password(password)
            # user.save()

            # ##creat the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name, last_name, username, email, password)
            user.save()
            messages.success(request, 'account registered successfully')
            return redirect('registerUser')
        
            

    else:
        form = UserForm()

    context = {
        'form' : form,
    }
    return render(request, 'accounts/registerUser.html', context)

