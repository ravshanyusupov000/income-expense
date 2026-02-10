from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Account
from .forms import AccountForm


class UserQuerysetMixin:
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class AccountListView(LoginRequiredMixin, UserQuerysetMixin, ListView):
    model = Account
    template_name = "finance/account_list.html"
    paginate_by = 20


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UserQuerysetMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account_list")


class AccountDeleteView(LoginRequiredMixin, UserQuerysetMixin, DeleteView):
    model = Account
    template_name = "finance/confirm_delete.html"
    success_url = reverse_lazy("finance:account_list")
