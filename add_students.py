import csv
from main.models import Student, User
from datetime import date

column_names = []
students = []

with open("list_of_students.csv", mode="r") as csvf:
    csv_reader = csv.DictReader(csvf, delimiter=',')
    line = 0

    for row in csv_reader:
        if row["Surname"] == "-":
            name = row["First name"]
        else:
            name = row["First name"] + " " + row["Surname"]

        email = row["Email address"]
        pushplata_user = User.objects.get(username="pushplata")

        d = date(year=2020, month=6, day=15)

        s = Student.objects.create(name=name, email=email, date_joined=d, grade=10, tutor=pushplata_user)
        print(s)
        s.save()
