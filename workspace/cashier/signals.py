# from django.db.models.signals import (
#     pre_save,
#     # post_save,
# )
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import CryptoInvoice


# @receiver(pre_save, sender=CryptoInvoice)
# def set_invoice_expire_date(sender, instance, **kwargs):
#     if not instance.expire_date:
#         instance.expire_date = \
#             timezone.now() + CryptoInvoice.TIMEOUT
