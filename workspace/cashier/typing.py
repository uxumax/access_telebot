import typing
from decimal import Decimal

Hash = str
Address = str


class ResponseTronContactTransaction(typing.Dict):
    example = {
        "ret": [{"contractRet": "SUCCESS", "fee": 27255900}],
        "signature": [
            Hash,
        ],
        "txID": Hash,
        "net_usage": 345,
        "raw_data_hex": Hash,
        "net_fee": 0,
        "energy_usage": 0,
        "blockNumber": 58286371,
        "block_timestamp": 1705493316000,
        "energy_fee": 27255900,
        "energy_usage_total": 64895,
        "raw_data": {
            "contract": [
                {
                    "parameter": {
                        "value": {
                            "data": Hash,
                            "owner_address": Address,
                            "contract_address": Address,
                        },
                        "type_url": "type.googleapis.com/protocol.TriggerSmartContract",
                    },
                    "type": "TriggerSmartContract",
                }
            ],
            "ref_block_bytes": "611d",
            "ref_block_hash": Hash,
            "expiration": 1705529300000,
            "fee_limit": 27396600,
            "timestamp": 1705493300000,
        },
        "internal_transactions": [],
    }


class DecodedTransaction(typing.TypedDict):
    txid: int
    amount: Decimal
    confirmations: int
