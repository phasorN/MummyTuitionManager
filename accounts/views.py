from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse

from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login

from accounts import forms

# Create your views here.
def userLogin(request):
	if(request.method == "GET"):
		return render(request, 'accounts/userLogin.html')
	elif(request.method == "POST"):

		next = reverse('main:index')
		# print('next' in request.GET)
		if 'next' in request.GET:
			next = request.GET.get('next')

		if request.POST.get('username'):
			username = request.POST.get('username')
			if request.POST.get('password'):
				password = request.POST.get('password')
				user = authenticate(request, username=username, password=password);
				if user is not None:
					login(request, user)
					return HttpResponseRedirect(next)
				else:
					return render(request, 'accounts/userLogin.html', {'errors': 'Invalid username or password'})
			else:
				return HttpResponseRedirect(reverse('accounts:login'))
		else:
			return HttpResponseRedirect(reverse('accounts:login'))		

class userRegistration(CreateView):
	model = User
	template_name = "accounts/userRegistration.html"
	form_class = forms.UserRegistrationForm
	success_url = reverse_lazy('accounts:registrationSuccess')

def registrationSuccess(request):
	return render(request, "accounts/registrationSuccess.html")

def userLogout(request):
	logout(request)
	return HttpResponseRedirect(reverse('main:index'))
