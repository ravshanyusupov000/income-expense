from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import hashlib, hmac
from django.conf import settings
from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    preferred_language = models.CharField(max_length=10, blank=True, default="")  # "uz", "ru", "en"

    def __str__(self):
        return f"Profile({self.user_id})"


class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        IN_PROGRESS = "in_progress", _("In Progress")
        CLOSED = "closed", _("Closed")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_tickets", verbose_name="User")
    subject = models.CharField(max_length=150, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")

    class Meta:
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"

    def __str__(self):
        return f"{self.subject} ({self.status})"

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Account(TimeStampedModel):
    class Kind(models.TextChoices):
        CASH = "cash", _("Cash")
        CARD = "card", _("Card")
        CURRENCY = "currency", _("Currency")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts", verbose_name="User")
    name = models.CharField(max_length=80, verbose_name="Account Name")
    kind = models.CharField(max_length=20, choices=Kind.choices, verbose_name="Account Type")
    currency = models.CharField(max_length=10, default="UZS", verbose_name="Currency")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Balance")

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return f"{self.name} ({self.currency})"

class Category(TimeStampedModel):
    class TxType(models.TextChoices):
        INCOME = "income", _("Income")
        EXPENSE = "expense", _("Expense")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name=_("User"),
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=80, verbose_name=_("Category Name"))
    tx_type = models.CharField(max_length=10, choices=TxType.choices, verbose_name=_("Transaction Type"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name", "tx_type"], name="uniq_category_per_user_or_global")
        ]
        ordering = ["tx_type", "name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.get_tx_type_display()}: {self.name}"

class Transaction(TimeStampedModel):
    class TxType(models.TextChoices):
        INCOME = "income", _("Income")
        EXPENSE = "expense", _("Expense")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions", verbose_name="User")
    tx_type = models.CharField(max_length=10, choices=TxType.choices, verbose_name="Type")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions", verbose_name="Account")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions", verbose_name="Category")
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Amount")
    date = models.DateField(verbose_name="Date")
    note = models.CharField(max_length=255, blank=True, verbose_name="Note")

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def clean(self):
        if self.category_id and self.tx_type != self.category.tx_type:
            from django.core.exceptions import ValidationError
            raise ValidationError(_("Category type does not match transaction type."))

    def __str__(self):
        return f"{self.get_tx_type_display()} {self.amount} - {self.date}"
