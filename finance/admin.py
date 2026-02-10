from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Category, Transaction, SupportTicket

User = get_user_model()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tx_type', 'user')
    list_filter = ('tx_type', 'user')
    search_fields = ('name',)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f != "user"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = None
        super().save_model(request, obj, form, change)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'category', 'account')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'created_at')