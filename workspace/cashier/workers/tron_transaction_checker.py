import requests
import typing
from decimal import Decimal
from time import sleep

from access_telebot.logger import get_logger
import cashier.models
import cashier.typing

from django.conf import settings


TRON_ADDRESS = "TFAEqAkD7AhFPazqmrUvVqyg39awDi9tNY"


class TronTransactionDataDecoder:
    def __init__(
        self, 
        transaction: cashier.typing.ResponseTronContactTransaction,
        current_block_number: int
    ):
        self.transaction = transaction
        self.current_block_number = current_block_number

    def decode(self):
        amount = self._decode_transaction_amount()
        confirmations = self._calc_confirmations()
        return {
            'txid': self.transaction["txID"],
            "amount": amount,
            "confirmations": confirmations,
        }

    def _decode_transaction_amount(self) -> Decimal:
        data_hex = self.transaction["raw_data"][
            "contract"
        ][0]["parameter"]["value"]["data"]
        amount_hex = data_hex[-64:]
        int_amount = int(amount_hex, 16)
        deciaml_amount = Decimal(int_amount) / Decimal('10') ** 6 
        return deciaml_amount

    def _calc_confirmations(self):
        return self.current_block_number - self.transaction["blockNumber"]


class TronTransactionsGetter:    
    @classmethod
    def get_all(cls, address: str) -> typing.List[
        cashier.typing.DecodedTransaction
    ]:
        current_block_number = cls._get_current_block_number()
        tron_transactions = cls._get_transactions(address)

        decoded_transactions = []
        for transaction in tron_transactions:
            if not cls._is_usdt_transaction(transaction):
                # skip all non USDT tranzes
                continue

            essential_tx_data: dict = TronTransactionDataDecoder(
                transaction, current_block_number
            ).decode()

            decoded_transactions.append(essential_tx_data)

        return decoded_transactions
    
    @staticmethod
    def _get_current_block_number() -> int:
        endpoint = f'{settings.TRON_API_URL}/v1/blocks/latest/events'
        response = requests.get(endpoint)
        if response.status_code == 200:
            current_block = response.json()
            return current_block["data"][0]["block_number"]
        else:
            raise Exception(f'Ошибка получения текущего блока: {response.status_code}')

    @staticmethod
    def _get_transactions(address: str):
        endpoint = f'{settings.TRON_API_URL}/v1/accounts/{address}/transactions'
        response = requests.get(endpoint)
        if response.status_code != 200:
            raise Exception(
                "Cannot get transactions for check confirmations. "
                f"Response status: {response.status_code}"
            )
        transactions = response.json()["data"]
        return transactions

    @staticmethod
    def _is_usdt_transaction(transaction):
        data = transaction["raw_data"]["contract"][0]["parameter"]["value"]
        if "contract_address" not in data:
            return False
        if settings.TRON_USDT_CONTRACT != data["contract_address"]:
            return False
        return True


class InvoiceTransactionChecker:
    def __init__(
        self, 
        invoice: cashier.models.CryptoInvoice, 
        last_transactions: typing.List[
            cashier.typing.DecodedTransaction
        ],
    ):
        self.invoice = invoice
        # self.last_transactions = last_transactions
        self.invoice_tx = self._get_invoice_transaction(
            invoice, last_transactions
        )

    def no_transaction(self) -> bool:
        return self.invoice_tx is None

    def no_confirmations(self) -> bool:
        return self.invoice_tx["confirmations"] == 0

    def not_enough_confirmations(self) -> bool:
        self._update_transaction_model()
        return self.\
            invoice_tx["confirmations"] < settings.TRON_CONFIRMATION_COUNT

    def _get_invoice_transaction(
        self, 
        invoice,
        transactions: typing.List[
            cashier.typing.DecodedTransaction
        ]
    ) -> typing.Optional[cashier.typing.DecodedTransaction]:
        for tx in transactions:
            
            if tx["confirmations"] == 0:
                continue
            
            if tx["amount"] == invoice.amount:
                return tx
        
        return None

    def _update_transaction_model(self):
        cashier.models.CryptoTransaction.objects.update_or_create(
            invoice=self.invoice,
            txid=self.invoice_tx["txid"],
            defaults={
                "current_confirmations": self.invoice_tx["confirmations"],
                "required_confirmations": settings.TRON_CONFIRMATION_COUNT
            }
        )


class TronTransactionCheckWorker:
    log = get_logger(__name__)

    def start_loop(self):
        while True:
            self._beat()
            sleep(60 * 3)  # 3 minutes

    def _beat(self):
        invoices = self._get_new_invoices()
        if not invoices:
            self.log.debug(
                "Do not have new invoices"
            )
            return

        for invoice in invoices:
            transactions = TronTransactionsGetter.get_all(invoice.address)
            self.log.debug(
                f"Got {len(transactions)} tron transactions from API "
                "for check invoice {invoice} payment"
            )
            
            checker = InvoiceTransactionChecker(
                invoice, transactions
            )

            if checker.no_transaction():
                self.log.debug(
                    f"No any transaction for invoice {invoice}"
                )
                continue

            if checker.no_confirmations():
                self.log.debug(
                    f"No any confirmations for invoice {invoice}"
                )
                continue

            if checker.not_enough_confirmations():
                self.log.debug(
                    f"Not enough confirmations for invoice {invoice}"
                )
                continue

            invoice.confirmed()
            self.log.info(
                f"Invoice {invoice} has been confirmed"
            )
    
    @staticmethod
    def _get_new_invoices():
        return cashier.models.CryptoInvoice.objects.filter(
            status="PAYING"
        ).all()


def start():
    TronTransactionCheckWorker().start_loop()
