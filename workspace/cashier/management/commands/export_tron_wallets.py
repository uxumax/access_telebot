from threading import Thread, Timer, Event
import sys
from django.core.management.base import BaseCommand
from cashier.models import TronAddress


class Command(BaseCommand):
    help = 'Export all TRON merchant wallets with private keys'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        wallets = TronAddress.objects.all() 

        if wallets.count() == 0:
            print("Still do not have any created TRON wallet")
            return

        for wallet in wallets:
            print("Address: ", wallet.address)
            print("Private Key: ", wallet.private_key)
            print("---")
        print("Completed! You can use these wallets in the TronLink Wallet app for fund withdrawals.")
        print("Simply copy and import these private keys to manage your funds like a regular crypto wallet app.")

