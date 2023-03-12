from django.urls import path
from django.conf.urls import url, include
from .views import expense_summary,expense_list, create_expense, CategoryList
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('expense_summary/<str:month>/', expense_summary, name='expense_summary'),
    path('expense_list/', expense_list, name='expense_list'),


    path('transactions/', create_expense, name='create_expense'),

    path('categories/', CategoryList.as_view()),
]
