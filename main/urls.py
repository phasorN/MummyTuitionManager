from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.Index, name = 'index'),
    path('student/new/', views.StudentCreateView.as_view(), name = 'student_form'),
    path('student/update/<int:pk>', views.StudentUpdateView.as_view(), name = 'student_update'),
    path('student/list/', views.StudentListView.as_view(), name = 'student_list'),
    path('student/<int:pk>/', views.StudentDetailView, name = 'student_detail'),
    path('student/discontinue/', views.StudentDiscontinueFormView, name = 'student_discontinue'),
    path('student/discontinue/mark/', views.StudentDiscontinueMarkView, name = 'student_discontinue_mark'),
    path('student/facts/', views.StudentFactsView, name="student_facts"),

    path('attendance/new/', views.AttendanceCreateView, name = 'attendance_form'),
    path('attendance/mark/', views.AttendanceMarkView, name = 'mark_attendance'),
    path('attendance/change/', views.AttendanceChangeView, name = 'change_attendance'),
    path('attendance/holiday/', views.AttendanceMarkHolidayView, name = 'mark_holiday'),
    path('attendance/not_holiday/', views.AttendanceMarkNotHolidayView, name = 'mark_not_holiday'),


    path('fee/new/', views.FeeCreateView, name='fee_form'),
    path('fee/update/', views.FeeUpdateView, name='fee_update'),
    path('fee/delete/', views.FeeDeleteView, name='fee_delete'),
    path('fee/list/', views.FeeListView.as_view(), name='fee_list'),
    # path('fee/update/<int:pk>/', views.FeeUpdateView, name='fee_update'),
]
