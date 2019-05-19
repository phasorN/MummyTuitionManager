from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.userLogin, name = 'login'),
    path('regSuccess/', views.registrationSuccess, name = 'registrationSuccess'),
    path('registration/', views.userRegistration.as_view(), name = 'registration'),
    path('logout/', views.userLogout, name = 'logout'),
]
