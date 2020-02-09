from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView
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
    # Show list of only those students who are active
    recent_fee_payments = Fee.objects.filter(tutor=request.user, student__active=True).order_by('-added_on')[:3]
    today = dt.datetime.now().date().strftime('%Y-%m-%d')

    return render(request, "main/index.html", {'date_today': today, 'recent_fee_payments': recent_fee_payments})


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    template_name = "main/student_form.html"
    form_class = StudentCreationForm
    success_url = reverse_lazy('main:student_list')

    def form_valid(self, form):
        form.instance.tutor = self.request.user
        return super().form_valid(form)


    def get_initial(self):
        initial = super().get_initial()
        date_f = dt.datetime.now().date()
        # date = dt.datetime(date_f)
        initial.update({ 'date_joined': date_f })
        return initial

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    template_name = "main/student_form.html"
    form_class = StudentCreationForm
    success_url = reverse_lazy('main:student_list')

    def form_valid(self, form):
        form.instance.tutor = self.request.user
        return super().form_valid(form)


    def get_initial(self):
        initial = super().get_initial()
        # date_f = dt.datetime.strptime('01-05-2018', "%d-%m-%Y")
        # date = dt.datetime(date_f)
        # initial.update({ 'date_joined': date_f })
        return initial

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "main/student_list.html"

    def get_queryset(self):
        return Student.objects.filter(active=True, tutor=self.request.user).order_by('grade', 'left')

@login_required
def StudentDetailView(request, pk):
    student = Student.objects.get(pk=pk)
    if student.tutor == request.user:
        if student.left:
            studentAttendance = Attendance.objects.filter(student=student, date__lt=student.date_left).order_by('-date')
        else:
            studentAttendance = Attendance.objects.filter(student=student).order_by('-date')
        feeDetails = Fee.objects.filter(tutor=request.user, student=student)
        # print(studentAttendance)
        context = {'studentAttendance': studentAttendance, 'feeDetails': feeDetails, 'student': student}
        return render(request, "main/student_detail.html", context)
    else:
        return render(request, "main/student_detail.html", {'error403': True})

@login_required
def StudentDiscontinueFormView(request):
    date = dt.datetime.now().date().strftime('%Y-%m-%d')
    students_class_10_1 = Student.objects.filter(active=True, tutor=request.user, grade=10.1, left=False)
    students_class_10 = Student.objects.filter(active=True, tutor=request.user, grade=10, left=False)
    return render(request, "main/student_discontinue_form.html", {'students_class_10_1':students_class_10_1, 'students_class_10':students_class_10, 'date': date})

@login_required
def StudentFactsView(request):
    if 'pk' in request.GET:
        pk = request.GET.get('pk')
        student = Student.objects.filter(active=True, pk=pk)
        if student.count() == 1:
            student = student.first()
            if student.tutor == request.user:
                data = {'code': 200, 'date_joined': student.date_joined.strftime("%d %B %Y"), 'grade': student.grade, }
                f = Fee.objects.filter(student = student).order_by('date_paid')
                if f.count():
                    data.update({'last_fee_date': str(f.last().date_paid.strftime("%d %B %Y"))})
                    return JsonResponse(data)
                else:
                    return JsonResponse(data)
            else:
                return JsonResponse({'code': 403, 'message': "Unauthorised. Please login with the account linked with this student."})
        else:
            return JsonResponse({'code': 404, 'message': "No student with pk = " +pk + " found."})
    else:
        return JsonResponse({'code': 400, 'message': "Bad Request. A GET argument 'pk' missing."})

@login_required
def StudentDiscontinueMarkView(request):
    if 'pk' in request.GET and 'date' in request.GET:
        pk = request.GET.get('pk')
        date = request.GET.get('date')
        if pk and date:
            student = Student.objects.filter(active=True, pk=pk)
            if student.count() == 1:
                student = student.first()
                if student.tutor == request.user:
                    student.left = True
                    # print(date)
                    date = dt.datetime.strptime(date, "%Y-%m-%d")
                    # print(date)
                    student.date_left = date
                    student.save()

                    # return JsonResponse({'code': 200})
                    return HttpResponseRedirect(reverse('main:student_detail', args=[pk]))
                else:
                    return JsonResponse({'code': 403,
                                         'message': "Unauthorised. Please login with the account linked with this student."})
            else:
                return JsonResponse({'code': 404, 'message': "No student with pk = " + pk + " found."})
        else:
            return JsonResponse({'code': 400, 'message': "Bad Request. A GET argument 'pk' or 'date' missing."})
    else:
        return JsonResponse({'code': 400, 'message': "Bad Request. A GET argument 'pk' or 'date' missing."})


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

        students = Student.objects.filter(active=True, tutor=request.user, grade=grade, left=False, date_joined__lte=date)

        noStudentsYet = False

        if students.count() == 0:
            noStudentsYet = True
            print("++++++++++++++++++++++++++++++" + str(students.count()))
            return render(request, "main/attendance_form.html", {'noStudentsYet': noStudentsYet, 'grade': grade, 'date': date})

        #########################################
        # Attendance models are created here.
        # (For this particular date)
        #########################################

        attendanceValues = {}

        markedHoliday = True

        for student in students:
            if Attendance.objects.filter(student=student, tutor=request.user, date=date).exists():
                # if attendence exists, get the value.
                a=Attendance.objects.get(student=student, tutor=request.user, date=date)
                attendanceValues.update({student.pk: a.value})
                if a.value != -5:
                    markedHoliday = False
            else:
                Attendance.objects.create(student=student, tutor=request.user, date=date, value=-1)
                a=Attendance.objects.get(student=student, tutor=request.user, date=date)
                attendanceValues.update({student.pk: a.value})

        date_minus = date - timedelta(1)
        date_plus = date + timedelta(1)
        if date == dt.datetime.now().date():
            date_plus = ""

        day = dt.datetime.strptime(request.GET.get('date'), '%Y-%m-%d').weekday()

        if day == 0:
            day = "Monday"
        elif day == 1:
            day = "Tuesday"
        elif day == 2:
            day = "Wednesday"
        elif day == 3:
            day = "Thursday"
        elif day == 4:
            day = "Friday"
        elif day == 5:
            day = "Saturday"
        elif day == 6:
            day = "Sunday"

        number_of_unmarked = 0

        for a in attendanceValues:
            if attendanceValues[a] == -1:
                number_of_unmarked = number_of_unmarked + 1

        return render(request, "main/attendance_form.html", {'students':students, 'date': date, 'day': day, 'grade': grade, 'attVal': attendanceValues, 'date_minus': date_minus, 'date_plus': date_plus, 'number_of_unmarked': number_of_unmarked, 'markedHoliday': markedHoliday})

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
def AttendanceMarkHolidayView(request):
    if request.GET.get('date') and request.GET.get('class'):
        grade = request.GET.get('class')
        date = request.GET.get('date')
        date = dt.datetime.strptime(date, '%Y-%m-%d').date()

        students = Student.objects.filter(active=True, tutor=request.user, grade=grade, left=False, date_joined__lte=date)

        for student in students:
            if Attendance.objects.filter(student=student, tutor=request.user, date=date).exists():
                a=Attendance.objects.get(student=student, tutor=request.user, date=date)
                a.value = -5
                a.save()
            else:
                Attendance.objects.create(student=student, tutor=request.user, date=date, value=-5)
        return AttendanceCreateView(request)

    return HttpResponse("<html><head><title>Mark Attendance</title><meta name='viewport' content='width=device-width, initial-scale=1.0'></head><h4>ERROR 400: BAD REQUEST.</h4><a href=" + reverse('main:index') + ">Go to home page</a></</html>")

@login_required
def AttendanceMarkNotHolidayView(request):
    if request.GET.get('date') and request.GET.get('class'):
        grade = request.GET.get('class')
        date = request.GET.get('date')
        date = dt.datetime.strptime(date, '%Y-%m-%d').date()

        students = Student.objects.filter(active=True, tutor=request.user, grade=grade, left=False, date_joined__lte=date)

        for student in students:
            if Attendance.objects.filter(student=student, tutor=request.user, date=date).exists():
                a=Attendance.objects.get(student=student, tutor=request.user, date=date)
                a.value = -1
                a.save()
            else:
                Attendance.objects.create(student=student, tutor=request.user, date=date, value=-1)
        return AttendanceCreateView(request)

    return HttpResponse("<html><head><title>Mark Attendance</title><meta name='viewport' content='width=device-width, initial-scale=1.0'></head><h4>ERROR 400: BAD REQUEST.</h4><a href=" + reverse('main:index') + ">Go to home page</a></</html>")


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
        students_class_10_1 = Student.objects.filter(active=True, tutor=request.user, grade=10.1, left=False)
        students_class_10 = Student.objects.filter(active=True, tutor=request.user, grade=10, left=False)
        return render(request, "main/fee_form.html", {'students_class_10_1': students_class_10_1,
                                                      'students_class_10': students_class_10,
                                                      'today': today,
                                                      'yesterday': yesterday})

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
                students_class_9 = Student.objects.filter(active=True, tutor=request.user, grade=9, left=False)
                students_class_10 = Student.objects.filter(active=True, tutor=request.user, grade=10, left=False)
                error = "You already added that '" + student.name + " paid Rs " + amount + " on " + date_paid + ".'"
                return render(request, "main/fee_details_duplicate.html", {'error_part1': error, 'error_part2':  'Do you want to add again?', 'date_paid': date_paid, 'amount':amount, 'pk': pk})
        else:
            added_on = dt.datetime.now()
            Fee.objects.create(tutor=request.user, student=student, date_paid=date_paid, amount=amount, added_on=added_on)
            fee = Fee.objects.get(tutor=request.user, student=student, date_paid=date_paid, amount=amount, added_on=added_on)

        return HttpResponseRedirect(reverse('main:index') + "?hover_id=" + str(fee.pk))


class FeeListView(LoginRequiredMixin, ListView):
    model = Fee
    template_name = "main/fee_list.html"

    def get_queryset(self):
        # Show list of only those students who are active
        return Fee.objects.filter(tutor=self.request.user, student__active=True).order_by('-added_on')
    def get_context_data(self, ** kwargs):
        context = super().get_context_data( ** kwargs)
        today = dt.datetime.now().date().strftime("%Y-%m-%d")
        yesterday = (dt.datetime.now().date() - timedelta(1)).strftime("%Y-%m-%d")
        context.update({'today': today, 'yesterday': yesterday})
        print(context)
        return context


@login_required
def FeeUpdateView(request):

    if request.method == "POST":
        date_paid = request.POST.get('date_paid')
        date_paid_new = request.POST.get('date_paid_new')
        pk = request.POST.get('pk')
        amount = request.POST.get('amount')
        amount_new = request.POST.get('amount_new')
        added_on = request.POST.get('added_on')
        student = Student.objects.get(pk=pk)

        fee = Fee.objects.get(tutor=request.user, student=student, date_paid=date_paid, amount=amount, added_on=added_on)
        fee.date_paid = date_paid_new
        fee.amount = amount_new
        fee.save()
        return HttpResponseRedirect(reverse('main:fee_list') + "?hover_id=" + str(fee.pk))

    else:
        # return HttpResponse(status=405, content="METHOD NOT ALLOWED")
        return HttpResponse("<html><head><title>Update Fee</title><meta name='viewport' content='width=device-width, initial-scale=1.0'></head><h4>ERROR 405: METHOD NOT ALLOWED.</h4><a href=" + reverse('main:index') + ">Go to home page</a></</html>")



@login_required
def FeeDeleteView(request):
    date_paid = request.GET.get('date_paid')
    pk = request.GET.get('pk')
    amount = request.GET.get('amount')
    added_on = request.GET.get('added_on')
    student = Student.objects.get(pk=pk)

    fee = Fee.objects.get(tutor=request.user, student=student, date_paid=date_paid, amount=amount, added_on=added_on)
    fee.delete()
    return HttpResponseRedirect(reverse('main:fee_list'))

