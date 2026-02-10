from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Category
from .forms import CategoryForm


class UserQuerysetMixin:
    def get_queryset(self):
        return super().get_queryset().filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        )

class CategoryListView(LoginRequiredMixin, UserQuerysetMixin, ListView):
    model = Category
    template_name = "finance/category_list.html"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        tx_type = self.request.GET.get("type")
        if tx_type in ("income", "expense"):
            qs = qs.filter(tx_type=tx_type)
        return qs


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:category_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UserQuerysetMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "finance/category_form.html"
    success_url = reverse_lazy("finance:category_list")


class CategoryDeleteView(LoginRequiredMixin, UserQuerysetMixin, DeleteView):
    model = Category
    template_name = "finance/confirm_delete.html"
    success_url = reverse_lazy("finance:category_list")
