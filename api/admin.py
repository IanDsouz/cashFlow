from django.contrib import admin
from .models import User, Budget, Income, Expense, Category, Account, Tag, SavingArea

class IncomeInline(admin.TabularInline):
    model = Income
    extra = 0

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0

class TagAdmin(admin.ModelAdmin):
    search_fields = ['name', 'category__name']
    list_filter = ['category', 'saving_area']
    ordering = ['name']
    list_display = ['name', 'category', 'notes', 'raw_description']

class ExpenseAdmin(admin.ModelAdmin):
    search_fields = ['tag__name']
    list_filter = ['category', 'account', ('date', admin.DateFieldListFilter)]  # Adding date range filter
    ordering = ['-date']
    list_display = ['description', 'amount', 'date', 'category', 'account']

class SavingAreaAdmin(admin.ModelAdmin):
    inlines = [ExpenseInline]

admin.site.register(Expense, ExpenseAdmin)

admin.site.register(User)
admin.site.register(Budget)
admin.site.register(Income)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Tag, TagAdmin)
admin.site.register(SavingArea, SavingAreaAdmin)