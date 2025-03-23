from rest_framework import generics
from rest_framework.response import Response
from ..models import Income, Expense
from ..serializers import IncomeSerializer, ExpenseSerializer
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.db.models import Sum, Q

# Income APIs

class IncomeListAPIView(generics.ListAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeDetailAPIView(generics.RetrieveAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeCreateAPIView(generics.CreateAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeUpdateAPIView(generics.UpdateAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class IncomeDeleteAPIView(generics.DestroyAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

# Expense APIs

class ExpenseListAPIView(generics.ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseDetailAPIView(generics.RetrieveAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseCreateAPIView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseUpdateAPIView(generics.UpdateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseDeleteAPIView(generics.DestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

# Additional APIs

@api_view(['GET'])
def get_monthly_income_total(request):
    """
    Get total income for the current month, considering date ranges.
    """
    today = datetime.today()

    # Filter incomes that either start in this month or span this month
    monthly_income_total = Income.objects.filter(
        Q(from_date__lte=today) & 
        Q(to_date__gte=today)
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({'monthly_income_total': monthly_income_total})

@api_view(['GET'])
def get_monthly_expense_total(request):
    """
    Get total expense for the current month, considering date ranges.
    """
    today = datetime.today()

    # Filter expenses where date falls within the current month and year
    monthly_expense_total = Expense.objects.filter(
        date__month=today.month,
        date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({'monthly_expense_total': monthly_expense_total})

@api_view(['GET'])
def get_income(request):
    """
    Get income for a specific year, or a specific month if provided.
    """
    year = int(request.query_params.get('year', datetime.today().year))
    month = request.query_params.get('month')

    income_total = 0

    # Filter incomes that overlap with the requested year
    incomes = Income.objects.filter(
        Q(from_date__year=year) | Q(to_date__year=year) |
        (Q(from_date__lte=f'{year}-12-31') & Q(to_date__gte=f'{year}-01-01'))
    )

    for income in incomes:
        from_date = income.from_date
        to_date = income.to_date or income.from_date
        monthly_amount = income.amount

        # Get the start and end of the valid range
        range_start = max(from_date, datetime(year, 1, 1).date())
        range_end = min(to_date, datetime(year, 12, 31).date())

        # If a month is specified, return monthly income
        if month:
            month = int(month)
            if range_start.year == year and range_start.month > month:
                continue
            if range_end.year == year and range_end.month < month:
                continue

            income_total += monthly_amount  # Since it's a single month, just return the amount

        # Otherwise, calculate total yearly income
        else:
            total_months_in_range = (range_end.year - range_start.year) * 12 + (range_end.month - range_start.month) + 1
            income_total += monthly_amount * total_months_in_range

    return Response({'income_total': income_total})

@api_view(['GET'])
def get_yearly_expense_total(request):
    """
    Get total expense for the current year, considering date ranges.
    """
    today = datetime.today()

    # Filter expenses where date falls within the current year
    yearly_expense_total = Expense.objects.filter(
        date__year=today.year
    ).aggregate(total=Sum('amount'))['total'] or 0

    return Response({'yearly_expense_total': yearly_expense_total})