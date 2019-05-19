from django.contrib import admin
from main.models import Student, Attendance, Fee

# Register your models here.
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Fee)