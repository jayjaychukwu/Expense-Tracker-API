from django.urls import path
from .views import ExpenseSummaryStats, IncomeSourceSummaryStats


urlpatterns = [
    path(
        "expense_category_data",
        ExpenseSummaryStats.as_view(),
        name="expense-category-summary",
    ),
    path(
        "income_sources_data",
        IncomeSourceSummaryStats.as_view(),
        name="income-sources-summary",
    ),
]
