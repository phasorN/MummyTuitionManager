from django.contrib import admin
from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.Index, name = 'index'),
    path('student/new/', views.StudentCreateView.as_view(), name = 'student_form'),
    path('student/list/', views.StudentListView.as_view(), name = 'student_list'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name = 'student_detail'),
    
    path('attendance/new/', views.AttendanceCreateView, name = 'attendance_form'),
    path('attendance/mark/', views.AttendanceMarkView, name = 'attendance_mark'),
]
