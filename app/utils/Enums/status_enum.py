from enum import Enum


class CampaignInfluencerStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class CampaignStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"


class GeneratedInfluencersStatus(str, Enum):
    GENERATED = "generated"
