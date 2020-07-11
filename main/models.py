from django.db import models
from django.contrib.auth.models import User
from datetime import datetime as dt
from django.core.validators import MaxValueValidator, MinValueValidator


class Student(models.Model):
	tutor = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
	name = models.CharField(max_length=200)
	email = models.EmailField(max_length=100, null=False)
	grade = models.IntegerField()
	date_joined = models.DateField(null=True)
	left = models.BooleanField(null=False, default=False)
	date_left = models.DateField(null=True)
	active = models.BooleanField(default=True)
	contact_number = models.PositiveIntegerField(null=True)

	def __str__(self):
		return self.name + "({})".format(self.email) + ":class:" + str(self.grade)


class Attendance(models.Model):
	tutor = models.ForeignKey(User, on_delete = models.CASCADE, null = False)
	student = models.ForeignKey(Student, on_delete = models.CASCADE, null = False)
	date = models.DateField()
	value = models.IntegerField()

	def __str__(self):
		return str(self.student.name) + ":class:" + str(self.student.grade) + ":date:" + str(self.date)


class Fee(models.Model):
	tutor = models.ForeignKey(User, on_delete = models.CASCADE, null = False)
	student = models.ForeignKey(Student, on_delete = models.CASCADE, null = False)
	date_paid = models.DateField()
	amount = models.IntegerField(default=0)
	added_on = models.DateTimeField()

	def __str__(self):
		return str(self.student.name) + ":" + str(self.date_paid) + ":" + str(self.amount) + ":added_on:" + str(self.added_on)