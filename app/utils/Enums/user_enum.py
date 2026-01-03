from enum import Enum


class SenderType(str, Enum):
    USER = "USER"
    AI = "AI"
    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"


class AccountType(str, Enum):
    USER = "user"
    BUSINESS = "business"


AI_IDENTITY = {
    "username": "iShout",
    "picture": "https://i.ibb.co/x624xwN/logo.png",
    "account_type": AccountType.BUSINESS.value,
}
