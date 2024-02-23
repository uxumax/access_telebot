from tronpy import Tron, Contract
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
import time
import requests
from decimal import Decimal

from cashier import models

TRONGRID_API_KEY = "85809ba2-ae5c-4f57-ae5d-6095e79395c7"
DEFAULT_FEE_LIMIT = 28_000_000
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


# def trx_to_sun(trx_amount):
#     """Convert TRX to SUN."""
#     return trx_amount * 1_000_000


# def sun_to_trx(sun_amount):
#     """Convert SUN to TRX."""
#     return sun_amount / 1_000_000


def create_tron_account():
    priv_key = PrivateKey.random()
    account = priv_key.public_key.to_base58check_address()
    return account, priv_key


def get_free_address_model():
    model = models.TronAddress.objects.filter(
        status="FREE"
    ).first()
    if model is None:
        address, private_key = create_tron_account()
        model = models.TronAddress.objects.create(
            address=address,
            private_key=private_key,
            status="BUSY"
        )
    return model


def send_usdt(
    from_address: str, 
    to_address: str, 
    amount: int,  
    private_key: str  
):
    client = Tron(HTTPProvider(api_key=TRONGRID_API_KEY))
    contract = client.get_contract(USDT_CONTRACT)
    txn = (
        contract.functions.transfer(to_address, amount * 10 ** 6)
        # .with_owner(private_key.public_key.to_hex())from_address
        .with_owner(from_address)
        .fee_limit(DEFAULT_FEE_LIMIT)  # OUT OF ENERGY can be when it's too low
        .build()
        .sign(private_key)
    )

    tx = txn.broadcast().wait()
    return tx

