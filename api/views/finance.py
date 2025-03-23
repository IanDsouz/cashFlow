from django.db.models import F, Sum, DecimalField, Q
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from rest_framework.response import Response
import calendar
from decimal import Decimal
from datetime import datetime
from ..models import Expense, Income

@api_view(['GET'])
def financial_summary(request):
    year = request.query_params.get('year')  # Get year (optional)
    month = request.query_params.get('month')  # Get month (optional)

    expense_filter = Expense.objects.all()
    income_filter = Income.objects.all()

    if year:
        year = int(year)
        expense_filter = expense_filter.filter(date__year=year)

    if month:
        month = int(month)
        expense_filter = expense_filter.filter(date__month=month)

    # Fix: Adjust income filtering logic
    if year:
        income_filter = Income.objects.filter(
            Q(from_date__year=year) | Q(to_date__year=year) |
            (Q(from_date__lte=f'{year}-12-31') & Q(to_date__gte=f'{year}-01-01'))
        )

    if month:
        # Ensure we include incomes spanning multiple months
        income_filter = income_filter.filter(
            Q(from_date__month__lte=month) & Q(to_date__month__gte=month)
        )

    # Calculate expenses (excluding savings)
    expenses = expense_filter.filter(is_saving=False).aggregate(
        total_expense=Coalesce(Sum(F('amount'), output_field=DecimalField()), Decimal(0))
    )['total_expense']

    # Calculate savings
    savings = expense_filter.filter(is_saving=True).aggregate(
        total_savings=Coalesce(Sum('amount'), Decimal(0))
    )['total_savings']

    # Calculate income with proper spanning logic
    income_total = 0
    for income in income_filter:
        from_date = income.from_date
        to_date = income.to_date or income.from_date  # If no end date, assume one-time income
        monthly_amount = income.amount

        # Define the valid range
        range_start = max(from_date, datetime(year, 1, 1).date()) if year else from_date
        range_end = min(to_date, datetime(year, 12, 31).date()) if year else to_date

        if month:
            # Include income if it falls in the requested month
            if range_start.year == year and range_start.month > month:
                continue
            if range_end.year == year and range_end.month < month:
                continue
            income_total += monthly_amount  # Single month, take full amount
        else:
            # Calculate total income for the year
            total_months_in_range = (range_end.year - range_start.year) * 12 + (range_end.month - range_start.month) + 1
            income_total += monthly_amount * total_months_in_range

    # If a specific month is requested, return only that month's data
    if month:
        net_savings = round(income_total - expenses, 2)
        return Response({
            'year': year,
            'month': calendar.month_name[month],
            'income': round(income_total, 2),
            'expenses': round(expenses, 2),
            'savings': round(savings, 2),
            'net_savings': net_savings
        })

    # If no specific year is provided, return totals for all years
    all_years_expenses = Expense.objects.all().filter(is_saving=False).aggregate(
        total_expense=Coalesce(Sum('amount'), Decimal(0))
    )['total_expense']

    all_years_savings = Expense.objects.all().filter(is_saving=True).aggregate(
        total_savings=Coalesce(Sum('amount'), Decimal(0))
    )['total_savings']

    # Calculate income for all years considering spanning logic
    all_years_income_total = 0
    for income in Income.objects.all():
        from_date = income.from_date
        to_date = income.to_date or income.from_date
        monthly_amount = income.amount

        # Total income considering all years, no need for year/month filters
        range_start = from_date
        range_end = to_date

        total_months_in_range = (range_end.year - range_start.year) * 12 + (range_end.month - range_start.month) + 1
        all_years_income_total += monthly_amount * total_months_in_range

    net_savings_all_years = round(all_years_income_total - all_years_expenses, 2)

    # For all months in a year, calculate the monthly data for all years combined
    monthly_data = []
    for month in range(1, 13):
        month_name = calendar.month_name[month]

        month_expenses = expense_filter.filter(date__month=month).aggregate(
            total_expense=Coalesce(Sum('amount'), Decimal(0))
        )['total_expense']

        month_savings = expense_filter.filter(date__month=month, is_saving=True).aggregate(
            total_savings=Coalesce(Sum('amount'), Decimal(0))
        )['total_savings']

        # Calculate income for the month considering spanning logic
        month_income_total = 0
        for income in income_filter:
            from_date = income.from_date
            to_date = income.to_date or income.from_date
            monthly_amount = income.amount

            range_start = max(from_date, datetime(year, 1, 1).date())
            range_end = min(to_date, datetime(year, 12, 31).date())

            if range_start.month > month or range_end.month < month:
                continue

            month_income_total += monthly_amount

        net_savings = round(month_income_total - month_expenses, 2)

        monthly_data.append({
            'name': month_name,
            'income': round(month_income_total, 2),
            'expenses': round(month_expenses, 2),
            'savings': round(month_savings, 2),
            'net_savings': net_savings
        })

    total_income = round(sum([m['income'] for m in monthly_data]), 2)
    total_expense = round(sum([m['expenses'] for m in monthly_data]), 2)
    total_savings = round(sum([m['savings'] for m in monthly_data]), 2)
    total_net_savings = round(total_income - total_expense, 2)

    return Response({
        'monthly_data': monthly_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_savings': total_savings,
        'total_net_savings': total_net_savings,
        'net_savings_all_years': net_savings_all_years,   # Net savings for all years
        'total_savings_all_years': round(all_years_savings, 2),  # Total savings for all years
        'total_income_all_years': round(all_years_income_total, 2),  # Total income for all years
        'total_expenses_all_years': round(all_years_expenses, 2)  # Total expenses for all years
    })
