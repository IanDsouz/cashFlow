from rest_framework import status
from django.http import HttpResponse
from rest_framework import serializers,viewsets
from django.http import JsonResponse
from django.db.models import Sum, Case, When, Value, IntegerField
from rest_framework import generics
from .models import Expense, Budget, Category, Tag, Account
from .serializers import ExpenseSerializer, BudgetSerializer, CategorySerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

def expense_summary(request, month):
    queryset = Expense.objects.filter(date__month=month)
    serializer = ExpenseSerializer(queryset, many=True)
    categories = Category.objects.all()
    expenses = Expense.objects.filter(date__month=month).values('category__name').annotate(total=Sum('amount'))
    total_expense = round(sum(float(expense['amount']) for expense in serializer.data), 2)

    category_expenses = []
    planned_budget = 0
    for category in categories:
        expense = next((x for x in expenses if x['category__name'] == category.name), None)
        if expense:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            planned_budget = planned_budget + round(budget.start_balance, 2)
            category_expenses.append({'name': category.name, 'total': round(expense['total'], 2), 'planned_expense': planned_expense})
        else:
            budget = Budget.objects.get(category=category)
            planned_expense = budget.start_balance
            planned_budget = planned_budget + round(budget.start_balance, 2)
            category_expenses.append({'name': category.name, 'total': 0, 'planned_expense': planned_expense})
    return JsonResponse({'expenses': category_expenses, 'total_expense': total_expense, 'planned_budget': planned_budget})


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def expense_list(request):
    category = request.query_params.get('category', None)
    month = request.query_params.get('month', None)

    expenses = Expense.objects.all()

    if category is not None:
        expenses = expenses.filter(category__name=category)

    if month is not None:
        expenses = expenses.filter(date__month=month)

    expenses_data = []
    for expense in expenses:
        expenses_data.append({
            'type': 'expenses',
            'id': str(expense.id),
            'date': expense.date.isoformat(),
            'amount': str(expense.amount),
            'tag_name': expense.tag.name,
            'category': expense.category.name,
            'payment_method': expense.payment_method,
            'account': expense.account.name,
        })

    return JsonResponse({
        'data': expenses_data
    })

@api_view(['POST'])
def create_expense(request):
    serializer = ExpenseSerializer(data=request.data)
    print(request.data)
    
    if serializer.is_valid():
        # Get the category and tag objects from the foreign keys
        category = get_object_or_404(Category, pk=request.data['category'])
        tag = get_object_or_404(Tag, pk=request.data['tag'])
        account = get_object_or_404(Account, pk=request.data['account'])
        print(tag, category, account)

        # # Create the expense object with the validated serializer data and related objects
        expense = serializer.save(category=category, tag=tag)

        # print(expense)

        # # Set the payment method based on the foreign key
        payment_method = request.data['payment_method']

        # # Set the payment method based on the foreign key
        account = request.data['account']
        # expense.payment_method = payment_method
        # expense.save()

        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)