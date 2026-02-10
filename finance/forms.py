from django import forms
from .models import Transaction, Category, Account
from django.db.models import Q

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "kind", "currency"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            cls = "form-select" if name in ("kind",) else "form-control"
            field.widget.attrs.update({"class": cls})


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["tx_type", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            cls = "form-select" if name == "tx_type" else "form-control"
            field.widget.attrs.update({"class": cls})

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["tx_type", "account", "category", "amount", "date", "note"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["account"].queryset = Account.objects.filter(user=user)
        self.fields["category"].queryset = Category.objects.filter(
            Q(user=user) | Q(user__isnull=True)
        )

        for name, field in self.fields.items():
            cls = "form-select" if name in ("tx_type", "account", "category") else "form-control"
            field.widget.attrs.update({"class": cls})

    def clean(self):
        cleaned = super().clean()
        tx_type = cleaned.get("tx_type")
        category = cleaned.get("category")
        if category and tx_type and category.tx_type != tx_type:
            raise forms.ValidationError("Kategoriya turi tranzaksiya turi bilan mos emas.")
        return cleaned
from django import forms
from django.utils.translation import gettext_lazy as _

class SupportForm(forms.Form):
    phone = forms.CharField(
        label=_("Phone number"),
        max_length=15,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "inputmode": "numeric",
            "pattern": "[0-9]+",
        }),
        error_messages={
            "required": _("Phone number is required"),
        }
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not phone.isdigit():
            raise forms.ValidationError(
                _("Only numbers are allowed")
            )
        return phone
