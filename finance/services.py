from decimal import Decimal
from django.db import transaction as db_transaction
import secrets
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import Transaction, Account


def apply_transaction_effect(tx: Transaction, *, reverse: bool = False) -> None:
    """
    reverse=False -> tx ta’sirini balansga qo‘shadi
    reverse=True  -> tx ta’sirini balansdan qaytaradi (edit/delete uchun)
    """
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
    # balans update
    from django.db.models import F
    sign = 1 if tx.tx_type == Transaction.TxType.INCOME else -1
    Account.objects.filter(pk=tx.account_id).update(balance=F("balance") + sign * tx.amount)
    return tx

from django.db import transaction as db_transaction
from django.db.models import F
from .models import Transaction, Account


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
    """
    instance = bazadagi eski tx
    new_tx   = form’dan kelgan, lekin hali saqlanmagan (commit=False)
    """
    # 1) eski ta’sirni qaytarib tashla
    Account.objects.filter(pk=instance.account_id).update(
        balance=F("balance") - _sign(instance.tx_type) * instance.amount
    )

    # 2) instanceni yangi qiymatlar bilan update qil
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
# ==============================================================



def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


@transaction.atomic
def create_login_otp(identifier: str) -> str:
    now = timezone.now()

    # RATE LIMIT: 60 soniya
    last = (
        LoginOTP.objects
        .filter(identifier=identifier, purpose=LoginOTP.PURPOSE_LOGIN)
        .order_by("-created_at")
        .first()
    )
    if last and (now - last.created_at).total_seconds() < 60:
        raise ValueError("RATE_LIMIT")

    # Eski kodlarni bekor qilish
    LoginOTP.objects.filter(
        identifier=identifier,
        purpose=LoginOTP.PURPOSE_LOGIN,
        is_used=False,
        expires_at__gt=now,
    ).update(is_used=True)

    code = generate_otp_code()

    LoginOTP.objects.create(
        identifier=identifier,
        code_hash=LoginOTP.hash_code(code),
        purpose=LoginOTP.PURPOSE_LOGIN,
        expires_at=now + timedelta(minutes=5),
    )
    return code
