from django.shortcuts import redirect, render
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages, auth
from .utils import send_verification_email, detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor

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

            # send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
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

            # send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

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

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your Account is activated')
        return redirect('myAccount')
    else:
        messages.error(request, 'invalid activation link')
        return redirect('myAccount')


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
    redirecturl = detectUser(user)
    return redirect(redirecturl)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def venDashboard(request):
    return render(request, 'accounts/venDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request, 'accounts/custDashboard.html') 



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
        else: 
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')


    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # This method checks if a given token is valid for a specific user. default_token_generator.check_token(user, token)
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid #we are storing this at the session, we will need the primary key to reset the password.
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password'] #['..name in the html..']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid') # the uid we saved in the session previosly in reset_password_validate() 
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request, 'Passwordo not match')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
