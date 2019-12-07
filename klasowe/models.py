from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import datetime


class ClassCode(models.Model):
    code = models.CharField(max_length=5)


class Role(models.Model):
    name = models.CharField(max_length=100)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pass_changed = models.BooleanField(default=False)
    role_fk = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    class_code_fk = models.ForeignKey(ClassCode, on_delete=models.CASCADE)


class Year(models.Model):
    year = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2099)], default=datetime.datetime.now().year)
    class_code_fk = models.ForeignKey(ClassCode, on_delete=models.CASCADE)


class MonthPayment(models.Model):
    student_fk = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_code_fk = models.ForeignKey(ClassCode, on_delete=models.CASCADE)
    month = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(9)])
    year_fk = models.ForeignKey(Year, on_delete=models.CASCADE)


class Event(models.Model):
    class_code = models.ForeignKey(ClassCode, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateField(blank=True, null=True)
    value = models.DecimalField(decimal_places=2, max_digits=6, validators=[MinValueValidator(0)])


class EventPayment(models.Model):
    event_fk = models.ForeignKey(Event, on_delete=models.CASCADE)
    student_fk = models.ForeignKey(Student, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)