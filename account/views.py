from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Account verification
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from account.models import Account
from .forms import RegistrationForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )

            # send user activation link
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string("account/account_verification_template.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.id)),
                "token": default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, to=[to_email]) 
            send_email.send()
            # messages.success(request, "Thanks for registering with us. We have sent you an email to activate your account.")
            return redirect(to=f'/account/login/?action=verification&email={email}')
    else:
        form = RegistrationForm()
    
    context = {
        "form": form
    }
    return render(request=request, template_name='account/register.html', context=context)


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user:
            auth.login(request, user)
            # messages.success(request=request, message="You are logged in!")
            return redirect('home')
        else:
            messages.error(request=request, message="Invalid login credentials!")
            redirect(to='login')

    return render(request=request, template_name='account/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request=request)
    return redirect(reverse('login'))


def activate(request, uidb64, token):
    try:
        # decode user id
        uid = urlsafe_base64_decode(uidb64).decode()
        # get the user
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # if token is valid then activate the user account
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request=request, message="Congratulations! Your account has been activated.")
        return redirect('login')

def reset_password_validate(request, uidb64, token):
    try:
        # decode user id
        uid = urlsafe_base64_decode(uidb64).decode()
        # get the user
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request=request, message="Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request=request, message="This link has been expired!")
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        data = request.POST
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        if new_password != confirm_password:
            messages.error(request=request, message="New Password and Confirm Password didn't match.")

        uid = request.session['uid']
        user = Account.objects.get(pk=uid)
        user.set_password(new_password)
        user.save()
        messages.success(request=request, message="Password reset successful!")
        return redirect('login')

    return render(request=request, template_name='account/reset_password.html')


@login_required(login_url='login')
def dashboard(request):
    return render(request=request, template_name='account/dashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = "Reset your Password"
            message = render_to_string("account/reset_password_template.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.id)),
                "token": default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, to=[to_email]) 
            send_email.send()

            messages.success(request=request, message="We have sent you a mail at " + email)
            return redirect(to='login')

        except Account.DoesNotExist:
            messages.success(request=request, message="Account Does not exists!")
            return redirect(to='register')
    return render(request=request, template_name='account/forgot-password.html')
