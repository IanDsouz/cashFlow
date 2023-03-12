from unicodedata import name
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.name

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='PKO')
    start_balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    end_balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    saved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.DateField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return  self.name

class Category(models.Model):
    name = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.name


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='PKO')
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=255, choices=[("Savings", "Savings"),
     ("Credit Card", "Credit Card"), ("Current", "Current"),("Invest", "Invest"), ("Spending", "Spending")], default='Savings')
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.name

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    income_type = models.CharField(max_length=255, choices=[("Salary", "Salary"),
     ("Bonus", "Bonus"), ("Freelancing", "Freelancing")], default='Salary')
    source = models.CharField(max_length=255,default="")
    date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    recurring = models.BooleanField(default=False)
    next_occurrence = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False,default='PKO')

    def __str__(self):
        return  self.income_type + ' - ' + str(self.amount)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default='')
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return  self.name + ' - ' + self.category.name


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,default=1,null=True) 
    notes = models.TextField(null=True, blank=True)
    recurring = models.BooleanField(default=False)
    next_occurrence = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=255, choices=[("Cash", "Cash"),
     ("Card", "Card"), ("Paypal", "Paypal")], default='Card')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='PKO')
    expense_reason = models.CharField(max_length=255, choices=[("Necessary", "Necessary"),
     ("Needed", "Needed"), ("not requred", "not requred")], default='Necessary')
    def __str__(self):
        return  self.category.name + ' - ' +self.tag.name + ' - ' + str(self.amount) + '-' + str(self.date)
