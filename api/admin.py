from django.contrib import admin
from .models import User, Budget, Income, Expense, Category, Account, Tag, SavingArea

class IncomeInline(admin.TabularInline):
    model = Income
    extra = 0

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0

class ExpenseAdmin(admin.ModelAdmin):
    search_fields = ['tag__name']

admin.site.register(Expense, ExpenseAdmin)

admin.site.register(User)
admin.site.register(Budget)
admin.site.register(Income)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Tag)
admin.site.register(SavingArea)