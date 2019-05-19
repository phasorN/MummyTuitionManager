from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from main.forms import StudentCreationForm
from main.models import Student
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

import datetime as dt

# Create your views here.
def Index(request):
	return render(request, "main/index.html", {})

class StudentCreateView(LoginRequiredMixin, CreateView):
	model = Student
	template_name = "main/student_form.html"
	form_class = StudentCreationForm
	success_url = reverse_lazy('main:student_form')

	def form_valid(self, form):
		form.instance.tutor = self.request.user
		return super().form_valid(form)


	def get_initial(self):
		initial = super().get_initial()
		date_f = dt.datetime.strptime('01-05-2018', "%d-%m-%Y")
		# date = dt.datetime(date_f)
		initial.update({ 'date_joined': date_f })
		return initial
	# return render(request, "main/student_form.html", {'form': StudentCreationForm})

class StudentListView(LoginRequiredMixin, ListView):
	model = Student
	template_name = "main/student_list.html"


class StudentDetailView(LoginRequiredMixin, DetailView):
	model = Student
	template_name = "main/student_detail.html"

@login_required
def AttendanceCreateView(request):

	date = dt.datetime.now().date()
	if 'date' in request.GET:
		date = request.GET.get('date')

	if request.GET.get('date') and request.GET.get('class'):
		grade = request.GET.get('class')
		date = request.GET.get('date')
		date = dt.datetime.strptime(date, '%Y-%m-%d').date()

		students = Student.objects.filter(tutor=request.user, grade=grade)
		return render(request, "main/attendance_form.html", {'students':students, 'date': date, 'grade': grade})

	date = dt.datetime.now().date()
	date = date.strftime('%Y-%m-%d')
	# print(date)
	return render(request, "main/date_class_form.html", {'date':date})

@login_required
def AttendanceMarkView(request):
	date = request.GET.get('date')
	pk = request.GET.get('pk')
	print(pk + ' ' + date)
	

	return JsonResponse({'code': 200})