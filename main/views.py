from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from main.forms import StudentCreationForm
from main.models import Student, Attendance, Fee
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

import datetime as dt
from datetime import timedelta

# Create your views here.
def Index(request):
	if not request.user.is_authenticated:
		return render(request, "main/index.html",{})

	# If user is logged in.
	recent_fee_payments = Fee.objects.filter(tutor=request.user).order_by('-added_on')[:5]
	today = dt.datetime.now().date().strftime('%Y-%m-%d')

	return render(request, "main/index.html", {'date_today': today, 'recent_fee_payments': recent_fee_payments})


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

	def get_queryset(self):
		return Student.objects.filter(tutor=self.request.user).order_by('grade')

class StudentDetailView(LoginRequiredMixin, DetailView):
	model = Student
	template_name = "main/student_detail.html"

	def get_context_data(self, ** kwargs):
		context = super().get_context_data( ** kwargs)
		pk=self.kwargs.get('pk')
		student = Student.objects.get(pk=pk)
		studentAttendance = Attendance.objects.filter(student=student).order_by('-date')
		feeDetails = Fee.objects.filter(tutor=self.request.user, student=student)
		# print(studentAttendance)
		context.update({'studentAttendance': studentAttendance, 'feeDetails': feeDetails})
		return context

@login_required
def AttendanceCreateView(request):

	date = dt.datetime.now().date()
	if 'date' in request.GET:
		date = request.GET.get('date')

	if request.GET.get('date') and request.GET.get('class'):
		grade = request.GET.get('class')
		date = request.GET.get('date')
		date = dt.datetime.strptime(date, '%Y-%m-%d').date()

		if date > dt.datetime.now().date():
			date = dt.datetime.now().date()
			date = date.strftime('%Y-%m-%d')

			context = {'date':date, 'error': 'Adding future attendances is not allowed.'}
			return render(request, "main/date_class_form.html", context)

		students = Student.objects.filter(tutor=request.user, grade=grade, left=False)

		#########################################
		# Attendance models are created here.
		# (For this particular date)
		#########################################

		attendanceValues = {}

		for student in students:
			if Attendance.objects.filter(student=student, tutor=request.user, date=date).exists():
				# if attendence exists, get the value.
				a=Attendance.objects.get(student=student, tutor=request.user, date=date)
				attendanceValues.update({student.pk: a.value})
			else:
				Attendance.objects.create(student=student, tutor=request.user, date=date, value=-1)
				a=Attendance.objects.get(student=student, tutor=request.user, date=date)
				attendanceValues.update({student.pk: a.value})
		
		date_minus = date - timedelta(1)
		date_plus = date + timedelta(1)
		# print(date_minus)
		# print(date_plus)
		
		number_of_unmarked = 0

		for a in attendanceValues:
			if attendanceValues[a] == -1:
				number_of_unmarked = number_of_unmarked + 1

		return render(request, "main/attendance_form.html", {'students':students, 'date': date, 'grade': grade, 'attVal': attendanceValues, 'date_minus': date_minus, 'date_plus': date_plus, 'number_of_unmarked': number_of_unmarked})

	date = dt.datetime.now().date()
	date = date.strftime('%Y-%m-%d')
	# print(date)
	return render(request, "main/date_class_form.html", {'date':date})

@login_required
def AttendanceMarkView(request):
	date = request.GET.get('date')
	pk = request.GET.get('pk')
	value = request.GET.get('value')

	date = dt.datetime.strptime(date, '%d-%m-%Y')

	student = Student.objects.get(pk=pk)
	a = Attendance.objects.get(student=student, tutor=request.user, date=date)

	a.value = int(value)
	a.save()

	return JsonResponse({'code': 200})

@login_required
def AttendanceChangeView(request):
	date = request.GET.get('date')
	pk = request.GET.get('pk')
	date = dt.datetime.strptime(date, '%d-%m-%Y')

	student = Student.objects.get(pk=pk)
	a = Attendance.objects.get(student=student, tutor=request.user, date=date)

	current_value = a.value
	# print(current_value)

	if current_value == 0:
		a.value = 1
		a.save()
		return JsonResponse({'code': 200, 'changedTo': 1})
	elif current_value ==1:
		a.value = 0
		a.save()
		return JsonResponse({'code': 200, 'changedTo': 0})
	else:
		return JsonResponse({'code': 400})
		
@login_required
def FeeCreateView(request):
	if request.method == "GET":

		today = dt.datetime.now().date().strftime("%Y-%m-%d")
		yesterday = (dt.datetime.now().date() - timedelta(1)).strftime("%Y-%m-%d")
		students_class_9 = Student.objects.filter(tutor=request.user, grade=9)
		students_class_10 = Student.objects.filter(tutor=request.user, grade=10)
		return render(request, "main/fee_form.html", {'students_class_9':students_class_9, 'students_class_10':students_class_10, 'today': today, 'yesterday': yesterday})

	elif request.method == "POST":	

		date_paid = request.POST.get('date_paid')
		amount = request.POST.get('amount')
		pk = request.POST.get('pk')
		student = Student.objects.get(pk=pk)

		if Fee.objects.filter(tutor=request.user, student=student, date_paid=date_paid, amount=amount).count() >= 1:
			if request.POST.get('add_again'):
				added_on = dt.datetime.now()
				fee = Fee.objects.create(tutor=request.user, student=student, date_paid=date_paid, amount=amount, added_on=added_on)
			else:
				today = dt.datetime.now().date().strftime("%Y-%m-%d")
				yesterday = (dt.datetime.now().date() - timedelta(1)).strftime("%Y-%m-%d")
				students_class_9 = Student.objects.filter(tutor=request.user, grade=9)
				students_class_10 = Student.objects.filter(tutor=request.user, grade=10)
				error = "You already added that '" + student.name + " paid Rs " + amount + " on " + date_paid + ".'"
				return render(request, "main/fee_details_duplicate.html", {'error_part1': error, 'error_part2':  'Do you want to add again?', 'date_paid': date_paid, 'amount':amount, 'pk': pk})
		else:
			added_on = dt.datetime.now()
			Fee.objects.create(tutor=request.user, student=student, date_paid=date_paid, amount=amount, added_on=added_on)
			fee = Fee.objects.get(tutor=request.user, student=student, date_paid=date_paid, amount=amount, added_on=added_on)
			
		return HttpResponseRedirect(reverse('main:index') + "?hover_id=" + str(fee.pk))