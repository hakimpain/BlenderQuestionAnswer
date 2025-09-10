from django.shortcuts import redirect, render
from .forms import RegistrationForm,LoginForm
from django.contrib import auth
from django.contrib import messages

# Create your views here.
def login_register(request):
    return render_page_with_forms(request)

def register(request):
    register_form = None
    if request.method == 'POST':
        register_form = RegistrationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            register_form = None
            messages.success(request,'You have successfully registered, please login with your new account to continue.')
            return redirect('login_registration')
    return render_page_with_forms(request,register_form=register_form)

def login(request):
    login_form = None
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            psw = login_form.cleaned_data['password']
            user = auth.authenticate(request,username=username,password=psw)
            if user:
                auth.login(request,user)
                return redirect('home')
        messages.error(request,'Incorrect Username or password...')
    return render_page_with_forms(request,login_form=login_form)

def logout(request):
    auth.logout(request)
    return redirect('home')

def render_page_with_forms(request,register_form=None,login_form=None):
    context = {
        'register_form': register_form if register_form else RegistrationForm(),
        'login_form': login_form if login_form else LoginForm()
    }
    return render(request,'LoginOrRegistration.html',context)
