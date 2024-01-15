from django.shortcuts import redirect, render
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages, auth
from . import utils
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.exceptions import PermissionDenied

# Restruct the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
    
# Restruct the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2 :
        return True
    else:
        raise PermissionDenied

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('myAccount')
    elif request.method == 'POST':
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
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'account registered successfully')
            return redirect('registerUser')
  
    else:
        form = UserForm()

    context = {
        'form' : form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('myAccount') 
    elif request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.userProfile = UserProfile.objects.get(user=user) # get the userprofile from user
            vendor.save()
            messages.success(request,  'account registered successfully')
            return redirect('registerVendor')
        else:
            print('invalid_______________')
            print(form.errors)

    else:
        v_form = VendorForm()
        form = UserForm()

    context={
        'form' : form,
        'v_form' : v_form
    }

    return render(request, 'accounts/registerVendor.html', context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('myAccount')
    elif request.method == "POST":
        email = request.POST['email'] # post['email'] email:name of the field in the html
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user) #login() is an auth function (built in)
            messages.success(request, 'you are logged in')
            return redirect('myAccount')
        else:
            messages.error(request, 'invalid user')
            return redirect('login')

    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'you are loged out')
    return redirect('login')

@login_required(login_url='login') #send the user to login page when he's not logged in
def myAccount(request):
    user = request.user
    redirecturl = utils.detectUser(user)
    return redirect(redirecturl)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def venDashboard(request):
    return render(request, 'accounts/venDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, 'accounts/custDashboard.html') 