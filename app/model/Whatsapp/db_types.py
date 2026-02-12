from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class CampaignInfluencerResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    platform: str
    followers: int | None = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
