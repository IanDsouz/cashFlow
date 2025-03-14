from django.urls import path
from django.conf.urls import url, include
from .views.expense import  ExpenseCreateAPIView, ExpenseRetrieveAPIView, ExpenseUpdateAPIView, ExpenseDeleteAPIView, ExpenseByCategoryAPIView, expense_summary, ExpenseUploadCreateAPIView, expense_all_year_monthly_total,expense_by_category, expense_by_category_total, expense_summary_top, expense_list, create_expense, CategoryList, expense_yearly_totals,expense_year_monthly_totals, expense_year_monthly, expenses_by_tag,LogoutView,ExpenseCheckTagsAPIView
from .views.saving_area import SavingAreaListCreateAPIView, SavingAreaDetailAPIView
from .views.tag import TagListAPIView,TagCreateAPIView 
from .views.finance import financial_summary


from .views.income import (
    IncomeListAPIView, IncomeDetailAPIView, IncomeCreateAPIView, 
    IncomeUpdateAPIView, IncomeDeleteAPIView,
    ExpenseDetailAPIView,
    get_monthly_income_total,
    get_income, get_yearly_expense_total, get_monthly_expense_total
)
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [

    path('incomes/yearly-total/', get_income, name='yearly-income-total'),
    path('expenses/yearly-total/', get_yearly_expense_total, name='yearly-expense-total'),

    path('expense_summary/<int:year>/<int:month>', expense_summary, name='expense_summary'),
    path('expense_summary_top/<int:year>/<int:month>', expense_summary_top, name='expense_summary_top'),
    path('expense/<int:year>/<str:category_name>/', expense_by_category, name='expense_by_category'),
    path('expense/<int:year>/<str:category_name>/<int:month>/', expense_by_category, name='expense_by_category_with_month'),
    path('expense/total/<int:from_year>/<int:to_year>/<str:category_name>/', expense_by_category_total, name='expense_by_category_total'),
    path('yearly_expense/<int:year>', expense_yearly_totals, name='expense_yearly_totals'),
    path('year_monthly_expense/<int:year>', expense_year_monthly, name='expense_year_monthly'),
    path('year_monthly_expense_total/<int:start_year>/', expense_year_monthly_totals, name='expense_year_monthly_totals'),
    path('expense_all_yearly_monthly_total/<int:start_year>/', expense_all_year_monthly_total, name='expense_all_year_monthly_total'),

    path('categories/', CategoryList.as_view()),
    path('expense/upload', ExpenseUploadCreateAPIView.as_view(), name='expense-create'),

    path('expense/check-tags', ExpenseCheckTagsAPIView.as_view(), name='expense-check-tags'),
    
    # # Second API: Create expenses after tags are resolved
    # path('expense/check-tags/', ExpenseCheckTagsAPIView.as_view(), name='expense-check-tags'),
    # path('expense/create/', ExpenseUploadCreateAPIView.as_view(), name='expense-create'),

        # Income URLs
    path('incomes/', IncomeListAPIView.as_view(), name='income-list'),
    path('incomes/<int:pk>/', IncomeDetailAPIView.as_view(), name='income-detail'),
    path('incomes/create/', IncomeCreateAPIView.as_view(), name='income-create'),
    path('incomes/<int:pk>/update/', IncomeUpdateAPIView.as_view(), name='income-update'),
    path('incomes/<int:pk>/delete/', IncomeDeleteAPIView.as_view(), name='income-delete'),

    # Expense URLs
    path('expenses/monthly-total/', get_monthly_expense_total, name='monthly-expense-total'),
    path('expenses/create/', ExpenseCreateAPIView.as_view(), name='expense-create'),

    path('expenses/<str:transaction_id>/', ExpenseRetrieveAPIView.as_view(), name='expense-retrieve'),  # Retrieve by transaction_id
    path('expenses/<str:id>/update/', ExpenseUpdateAPIView.as_view(), name='expense-update'),  # Update expense by transaction_id
    path('expenses/<str:id>/delete/', ExpenseDeleteAPIView.as_view(), name='expense-delete'),  # Delete expense by transaction_id
    path('expenses/', expense_list, name='expense_list'),
    path('expenses/category/<int:category_id>/', ExpenseByCategoryAPIView.as_view(), name='expense-by-category'),  # List expenses by category
    path('expenses/create/', ExpenseCreateAPIView.as_view(), name='expense-create'),
 

    # Additional URLs
    path('incomes/monthly-total/', get_monthly_income_total, name='monthly-income-total'),



    path('saving_areas/', SavingAreaListCreateAPIView.as_view(), name='saving_area-list-create'),
    path('saving_areas/<int:pk>/', SavingAreaDetailAPIView.as_view(), name='saving_area-detail'),

    #Tag URLs
    path('tags/', TagListAPIView.as_view(), name='tag-list'),
    path('tags/create/', TagCreateAPIView.as_view(), name='tag-create'),


    #finance summary
    path('financial-summary/', financial_summary, name='finance-summary'),
]