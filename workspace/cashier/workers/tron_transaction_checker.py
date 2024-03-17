import requests
import typing
from decimal import Decimal
from time import sleep

from main.workers import core
from access_telebot.logger import get_logger
from cashier import models
import cashier.types

from django.conf import settings


log = get_logger(__name__)


USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


class TronTransactionDataDecoder:
    # pprint(transaction)  # Example of transaction
    # {'block': 59000000,
    #  'block_ts': 1700000000000,
    #  'confirmed': True,
    #  'contractRet': 'SUCCESS',
    #  'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
    #  'contract_type': 'trc20',
    #  'finalResult': 'SUCCESS',
    #  'fromAddressIsContract': False,
    #  'from_address': 'TO6yKgS000000000000000000000000000',
    #  'from_address_tag': {},
    #  'quant': '5000000',
    #  'revert': False,
    #  'riskTransaction': False,
    #  'status': 0,
    #  'toAddressIsContract': False,
    #  'to_address': 'TFAEqA0000000000000000000000000000',
    #  'to_address_tag': {},
    #  'tokenInfo': {'issuerAddr': 'THPvaUhoh2Qn2y9THCZML3H815hhFhn5YC',
    #                'tokenAbbr': 'USDT',
    #                'tokenCanShow': 1,
    #                'tokenDecimal': 6,
    #                'tokenId': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
    #                'tokenLevel': '2',
    #                'tokenLogo': 'https://static.tronscan.org/production/logo/usdtlogo.png',
    #                'tokenName': 'Tether USD',
    #                'tokenType': 'trc20',
    #                'vip': True},
    #  'transaction_id': '80a0000000000000000000000000000000000000000000000000000000000000'}

    def __init__(
        self, 
        transaction: cashier.types.ResponseTronContactTransaction,
        current_block_number: int
    ):
        self.transaction = transaction
        self.current_block_number = current_block_number

    def decode(self):
        amount = self._decode_transaction_amount()
        confirmations = self._calc_confirmations()
        return {
            'txid': self.transaction["transaction_id"],
            "amount": amount,
            "confirmations": confirmations,
        }

    def _decode_transaction_amount(self) -> Decimal:
        # data_hex = self.transaction["raw_data"][
        #     "contract"
        # ][0]["parameter"]["value"]["data"]
        # amount_hex = data_hex[-64:]
        # int_amount = int(amount_hex, 16)
        int_amount = self.transaction["quant"]
        deciaml_amount = Decimal(int_amount) / Decimal('10') ** 6 
        return deciaml_amount

    def _calc_confirmations(self):
        return self.current_block_number - self.transaction["block"]


class TronTransactionsGetter:    
    @classmethod
    def get_all(cls, address: str) -> typing.List[
        cashier.types.DecodedTransaction
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
        API_HOST = "https://api.trongrid.io"
        endpoint = f'{API_HOST}/v1/blocks/latest/events'
        response = requests.get(endpoint)
        if response.status_code == 200:
            current_block = response.json()
            return current_block["data"][0]["block_number"]
        else:
            raise Exception(f'Ошибка получения текущего блока: {response.status_code}')

    @staticmethod
    def _get_transactions(address: str):
        API_HOST = "https://apilist.tronscanapi.com/api"
        endpoint = (
            f"{API_HOST}/new/token_trc20/transfers"
            f"?contract_address={USDT_CONTRACT}"
            f"&toAddress={address}"
            "&confirm="
        )
        log.debug(endpoint)
        response = requests.get(endpoint)
        if response.status_code != 200:
            raise Exception(
                "Cannot get transactions for check confirmations. "
                f"Response status: {response.status_code}"
            )
        # log.debug(f"{response.json()}")
        transactions = response.json()["token_transfers"]
        return transactions

    @staticmethod
    def _is_usdt_transaction(transaction):
        if "contract_address" not in transaction:
            return False
        if USDT_CONTRACT != transaction["contract_address"]:
            return False
        return True


class InvoiceTransactionChecker:
    def __init__(
        self, 
        invoice: models.CryptoInvoice, 
        last_transactions: typing.List[
            cashier.types.DecodedTransaction
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
            cashier.types.DecodedTransaction
        ]
    ) -> typing.Optional[cashier.types.DecodedTransaction]:
        for tx in transactions:
            if tx["confirmations"] == 0:
                continue
            
            if tx["amount"] == invoice.amount:
                return tx
        
        return None

    def _update_transaction_model(self):
        models.CryptoTransaction.objects.update_or_create(
            invoice=self.invoice,
            txid=self.invoice_tx["txid"],
            defaults={
                "current_confirmations": self.invoice_tx["confirmations"],
                "required_confirmations": settings.TRON_CONFIRMATION_COUNT
            }
        )


class Worker(core.Worker):
    beat_interval = 60 * 1
    stat = models.TronTransactionCheckerWorkerStat

    def start(self):
        while not self.stop_event.is_set():
            try:
                self._beat()
                self.wait()
            except Exception as e:
                log.exception(e)
                break

        log.warning(f"Worker:{__name__} has been stopped")
        return

    def _beat(self):
        invoices = self._get_new_invoices()
        if not invoices:
            log.debug(
                "Do not have new invoices"
            )
            return

        for invoice in invoices:
            transactions = TronTransactionsGetter.get_all(invoice.address)
            log.debug(
                f"Got {len(transactions)} tron transactions from API "
                f"for check invoice {invoice} payment"
            )
            
            checker = InvoiceTransactionChecker(
                invoice, transactions
            )

            if checker.no_transaction():
                log.debug(
                    f"No any transaction for invoice {invoice}"
                )
                continue

            if checker.no_confirmations():
                log.debug(
                    f"No any confirmations for invoice {invoice}"
                )
                continue

            if checker.not_enough_confirmations():
                log.debug(
                    f"Not enough confirmations for invoice {invoice}"
                )
                continue

            invoice.confirmed()
            log.info(
                f"Invoice {invoice} has been confirmed"
            )
    
    @staticmethod
    def _get_new_invoices():
        return models.CryptoInvoice.objects.filter(
            status__in=["PAYING", "PAID"]
        ).all()


