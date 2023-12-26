from django.urls import path
from django.conf.urls import url, include
from .views import expense_summary, expense_summary_top, expense_list, create_expense, CategoryList, ExpenseCreateAPIView, expense_yearly_totals,expense_year_monthly_totals, expense_year_monthly, expenses_by_tag,LogoutView
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    path('expense_summary/<int:year>/<int:month>', expense_summary, name='expense_summary'),
    path('expense_summary_top/<int:year>/<int:month>', expense_summary_top, name='expense_summary_top'),
    path('yearly_expense/<int:year>', expense_yearly_totals, name='expense_yearly_totals'),
    path('year_monthly_expense/<int:year>', expense_year_monthly, name='expense_year_monthly'),
    path('year_monthly_expense_total/<int:start_year>/', expense_year_monthly_totals, name='expense_year_monthly_totals'),
    path('expense_list/', expense_list, name='expense_list'),
    path('categories/', CategoryList.as_view()),
    path('expense', ExpenseCreateAPIView.as_view(), name='expense-create'),
    path('expenses_by_tag', expenses_by_tag, name='expenses_by_tag'),
]
