from enum import Enum


class CampaignInfluencerStatus(str, Enum):
    approved = "approved"
    rejected = "rejected"
    pending = "pending"


class CampaignStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"


class GeneratedInfluencersStatus(str, Enum):
    GENERATED = "generated"
