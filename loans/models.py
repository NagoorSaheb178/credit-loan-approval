from django.db import models
from datetime import date

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_income = models.FloatField()
    approved_limit = models.FloatField()
    current_debt = models.FloatField(default=0)

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='ACTIVE')
