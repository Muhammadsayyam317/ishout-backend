from enum import Enum


class CampaignInfluencerStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class GeneratedInfluencersStatus(str, Enum):
    GENERATED = "generated"
