from django.contrib import admin
from .models import (
    ClassCode,
    Role,
    Student,
    Year,
    MonthPayment,
    Event,
    EventPayment
)

# Register your models here.
admin.site.register(ClassCode)
admin.site.register(Role)
admin.site.register(Student)
admin.site.register(Year)
admin.site.register(MonthPayment)
admin.site.register(Event)
admin.site.register(EventPayment)