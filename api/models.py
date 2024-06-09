from unicodedata import name
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return  self.name

class SavingArea(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='Ian')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(default=1)
    completion_date = models.DateField(null=True, blank=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("completed", "Completed"),
        ],
        default="active",
    )
    icon = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='Ian')
    start_balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    month = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=True)
    saving_area = models.ForeignKey(SavingArea, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return  self.name

class Category(models.Model):
    name = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    saving_area = models.ForeignKey(SavingArea, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return  self.name

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='Ian')
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=255, choices=[("Savings", "Savings"),
     ("Credit Card", "Credit Card"), ("Current", "Current"),("Invest", "Invest"), ("Spending", "Spending")], default='Savings')
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    saving_area = models.ForeignKey(SavingArea, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return  self.name

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    income_type = models.CharField(max_length=255, choices=[("Salary", "Salary"),
     ("Bonus", "Bonus"), ("Freelancing", "Freelancing")], default='Salary')
    source = models.CharField(max_length=255,default="")
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    recurring = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    next_occurrence = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False,default='Ian')

    def __str__(self):
        return  self.income_type + ' - ' + str(self.amount)

class Tag(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default='')
    notes = models.TextField(null=True, blank=True)
    raw_description = models.TextField(null=True, blank=True)
    saving_area = models.ForeignKey(SavingArea, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f'{self.name} - {self.category.name}'

class Expense(models.Model):
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,default=1,null=True) 
    notes = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    recurring = models.BooleanField(default=False)
    next_occurrence = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=255, choices=[("Cash", "Cash"),
     ("Card", "Card"), ("Paypal", "Paypal")], default='Card')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    statement_text = models.TextField(null=True, blank=True)
    saving_area = models.ForeignKey(SavingArea, on_delete=models.SET_NULL, null=True, blank=True)
    is_saving = models.BooleanField(default=False)

    def __str__(self):
        return  self.category.name + ' - ' +self.tag.name + ' - ' + str(self.amount) + '-' + str(self.date)
