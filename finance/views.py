from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView, CreateView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Transaction
from .forms import TransactionForm
import json
from django.db.models import Sum, Count
from .models import Transaction, Account, Category
from django.views.generic import UpdateView, DeleteView
from .services import update_tx, delete_tx,create_tx
from datetime import timedelta, date
from django.utils.translation import gettext as _
from django.shortcuts import render
from .fx import get_cbu_rates


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:tx_list")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).select_related("account", "category")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        create_tx(tx=obj)
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "finance/confirm_delete.html"
    success_url = reverse_lazy("finance:tx_list")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        delete_tx(instance=self.object)
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "finance/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        range_ = self.request.GET.get("range", "month")
        today = timezone.localdate()
        if range_ == "day":
            start = today
        elif range_ == "week":
            start = today - timedelta(days=6)
        elif range_ == "year":
            start = date(today.year, 1, 1)
        else:  # month
            start = today.replace(day=1)
            range_ = "month"

        qs = Transaction.objects.filter(user=user, date__range=[start, today])
        income = qs.filter(tx_type="income").aggregate(s=Sum("amount"))["s"] or 0
        expense = qs.filter(tx_type="expense").aggregate(s=Sum("amount"))["s"] or 0

        balance = Account.objects.filter(user=user).aggregate(s=Sum("balance"))["s"] or 0

        LABELS = {
            "day": _("Day"),
            "week": _("Week"),
            "month": _("Month"),
            "year": _("Year"),
        }

        ctx.update({
            "range": range_,
            "range_label": LABELS.get(range_, _("Month")),
            "income_sum": income,
            "expense_sum": expense,
            "profit": income - expense,
            "balance": balance,
            "tx_count": qs.count(),
        })

        daily = qs.values("date", "tx_type").annotate(total=Sum("amount")).order_by("date")

        net = {}
        for r in daily:
            d = r["date"].isoformat()
            net.setdefault(d, 0)
            net[d] += r["total"] if r["tx_type"] == "income" else -r["total"]

        labels, data, acc = [], [], 0
        for d in sorted(net.keys()):
            acc += net[d]
            labels.append(d)
            data.append(float(acc))

        ctx["line_labels"] = json.dumps(labels)
        ctx["line_data"] = json.dumps(data)
        ctx["bar_labels"] = json.dumps(labels)
        ctx["bar_data"] = json.dumps([float(net[d]) for d in labels])
        cats = (qs.filter(tx_type="expense")
                .values("category__name")
                .annotate(total=Sum("amount"))
                .order_by("-total")[:6])

        ctx["donut_labels"] = json.dumps([c["category__name"] for c in cats])
        ctx["donut_data"] = json.dumps([float(c["total"]) for c in cats])

        try:
            ctx["fx"] = get_cbu_rates()
        except Exception:
            ctx["fx"] = {}

        return ctx
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/transaction_list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = (super().get_queryset()
              .filter(user=self.request.user)
              .select_related("account", "category"))

        tx_type = self.request.GET.get("type")
        if tx_type in ("income", "expense"):
            qs = qs.filter(tx_type=tx_type)

        dfrom = self.request.GET.get("from")
        dto = self.request.GET.get("to")
        if dfrom:
            qs = qs.filter(date__gte=dfrom)
        if dto:
            qs = qs.filter(date__lte=dto)

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(note__icontains=q) | Q(category__name__icontains=q) | Q(account__name__icontains=q))

        return qs

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:tx_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        create_tx(tx=obj)
        return super().form_valid(form)


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = "finance/report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        range_ = self.request.GET.get("range", "month")
        today = timezone.localdate()

        if range_ == "day":
            start = today
        elif range_ == "week":
            start = today - timedelta(days=6)
        elif range_ == "year":
            start = date(today.year, 1, 1)
        else:
            start = today.replace(day=1)
            range_ = "month"

        qs = Transaction.objects.filter(user=user, date__range=[start, today])

        income = qs.filter(tx_type="income").aggregate(s=Sum("amount"))["s"] or 0
        expense = qs.filter(tx_type="expense").aggregate(s=Sum("amount"))["s"] or 0
        profit = income - expense
        rows = {}
        for r in (qs.values("date", "tx_type").annotate(total=Sum("amount")).order_by("date")):
            d = r["date"].isoformat()
            rows.setdefault(d, {"date": d, "income": 0, "expense": 0, "net": 0})
            if r["tx_type"] == "income":
                rows[d]["income"] = float(r["total"] or 0)
            else:
                rows[d]["expense"] = float(r["total"] or 0)
        table = []
        labels, net_data = [], []
        for d in sorted(rows.keys()):
            income_v = rows[d]["income"]
            expense_v = rows[d]["expense"]
            net_v = income_v - expense_v
            rows[d]["net"] = net_v
            table.append(rows[d])
            labels.append(d)
            net_data.append(net_v)

        ctx.update({
            "range": range_,
            "start": start,
            "end": today,
            "income_sum": income,
            "expense_sum": expense,
            "profit": profit,

            "table": table,
            "chart_labels": json.dumps(labels),
            "chart_data": json.dumps(net_data),
        })
        return ctx
