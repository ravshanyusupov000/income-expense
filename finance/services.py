from decimal import Decimal
from django.db import transaction as db_transaction
import secrets
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import Transaction, Account
from django.db.models import F



def apply_transaction_effect(tx: Transaction, *, reverse: bool = False) -> None:
    sign = Decimal("1")
    if tx.tx_type == Transaction.TxType.EXPENSE:
        sign = Decimal("-1")

    if reverse:
        sign = -sign

    Account.objects.filter(pk=tx.account_id).update(balance=models.F("balance") + sign * tx.amount)


@db_transaction.atomic
def create_transaction(tx: Transaction) -> Transaction:
    tx.full_clean()
    tx.save()
    from django.db.models import F
    sign = 1 if tx.tx_type == Transaction.TxType.INCOME else -1
    Account.objects.filter(pk=tx.account_id).update(balance=F("balance") + sign * tx.amount)
    return tx

def _sign(tx_type: str) -> int:
    return 1 if tx_type == Transaction.TxType.INCOME else -1


@db_transaction.atomic
def create_tx(*, tx: Transaction) -> Transaction:
    tx.full_clean()
    tx.save()
    Account.objects.filter(pk=tx.account_id).update(balance=F("balance") + _sign(tx.tx_type) * tx.amount)
    return tx


@db_transaction.atomic
def update_tx(*, instance: Transaction, new_tx: Transaction) -> Transaction:
    Account.objects.filter(pk=instance.account_id).update(
        balance=F("balance") - _sign(instance.tx_type) * instance.amount
    )

    instance.tx_type = new_tx.tx_type
    instance.account_id = new_tx.account_id
    instance.category_id = new_tx.category_id
    instance.amount = new_tx.amount
    instance.date = new_tx.date
    instance.note = new_tx.note

    instance.full_clean()
    instance.save()
    Account.objects.filter(pk=instance.account_id).update(
        balance=F("balance") + _sign(instance.tx_type) * instance.amount
    )
    return instance


@db_transaction.atomic
def delete_tx(*, instance: Transaction) -> None:
    Account.objects.filter(pk=instance.account_id).update(
        balance=F("balance") - _sign(instance.tx_type) * instance.amount
    )
    instance.delete()