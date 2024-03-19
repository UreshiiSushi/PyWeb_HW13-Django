from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm, ProfileForm


def login_user(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        user = authenticate(
            username=request.POST["username"], password=request.POST["password"]
        )
        if user is None:
            messages.error(request, "Username or password didn't match")
            return redirect(to="members:login")

        login(request, user)
        return redirect(to="/")

    return render(request, "authenticate/login.html", context={"form": LoginForm()})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("Yoy Were Logged Out"))
    return redirect(to="/")


def register_user(request):
    if request.user.is_authenticated:
        return redirect(to="/")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="/")
        else:
            return render(
                request, "authenticate/register_user.html", context={"form": form}
            )

    return render(
        request, "authenticate/register_user.html", context={"form": RegisterForm()}
    )


@login_required
def profile(request):
    if request.method == "POST":
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile is updated successfully")
            return redirect(to="members:profile")

    profile_form = ProfileForm(instance=request.user.profile)
    return render(request, "authenticate/profile.html", {"profile_form": profile_form})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "authenticate/password_reset.html"
    email_template_name = "authenticate/password_reset_email.html"
    html_email_template_name = "authenticate/password_reset_email.html"
    success_url = reverse_lazy("members:password_reset_done")
    success_message = (
        "An email with instructions to reset your password has been sent to %(email)s."
    )
    subject_template_name = "authenticate/password_reset_subject.txt"
