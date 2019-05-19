from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
	tutor = models.ForeignKey(User, on_delete = models.CASCADE, null = False)
	name = models.CharField(max_length = 200)
	grade = models.IntegerField()
	date_joined = models.DateField(null = True)
	last_fee_month = models.IntegerField(null = True)

	def __str__(self):
		return self.name + ":class:" + str(self.grade)

class Attendance(models.Model):
	tutor = models.ForeignKey(User, on_delete = models.CASCADE, null = False)
	student = models.ForeignKey(Student, on_delete = models.CASCADE, null = False)
	date = models.DateField()
	value = models.IntegerField()

class Fee(models.Model):
	tutor = models.ForeignKey(User, on_delete = models.CASCADE, null = False)
	student = models.ForeignKey(Student, on_delete = models.CASCADE, null = False)
	date_paid = models.DateField()