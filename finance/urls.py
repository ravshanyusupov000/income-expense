from django.urls import path
from django.shortcuts import redirect

from .views import (
    DashboardView, TransactionListView, TransactionCreateView, ReportView,
    TransactionUpdateView, TransactionDeleteView
)
from .views_accounts import AccountListView, AccountCreateView, AccountUpdateView, AccountDeleteView
from .views_categories import CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView
from .views_support import support_quick_create

app_name = "finance"

def home(request):
    return redirect("finance:dashboard")

urlpatterns = [
    path("", home),

    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    path("tx/", TransactionListView.as_view(), name="tx_list"),
    path("tx/add/", TransactionCreateView.as_view(), name="tx_add"),
    path("tx/<int:pk>/edit/", TransactionUpdateView.as_view(), name="tx_edit"),
    path("tx/<int:pk>/delete/", TransactionDeleteView.as_view(), name="tx_delete"),

    path("report/", ReportView.as_view(), name="report"),

    path("accounts/", AccountListView.as_view(), name="account_list"),
    path("accounts/add/", AccountCreateView.as_view(), name="account_add"),
    path("accounts/<int:pk>/edit/", AccountUpdateView.as_view(), name="account_edit"),
    path("accounts/<int:pk>/delete/", AccountDeleteView.as_view(), name="account_delete"),

    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/add/", CategoryCreateView.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category_delete"),

    path("support/quick/", support_quick_create, name="support_quick"),
]
