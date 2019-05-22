from django.db import models
from django.contrib.auth.models import User
from datetime import datetime as dt

class Student(models.Model):
	tutor = models.ForeignKey(User, on_delete = models.CASCADE, null = False)
	name = models.CharField(max_length = 200)
	grade = models.IntegerField()
	date_joined = models.DateField(null = True)
	last_fee_month = models.IntegerField(null = True)
	left = models.BooleanField(default=False)
	date_left = models.DateField(null = True)

	def __str__(self):
		return self.name + ":class:" + str(self.grade)
	def studentLeft(self, date):
		self.left = True
		self.date_left = date
		self.save()

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