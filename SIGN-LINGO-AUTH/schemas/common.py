from typing import Annotated
from pydantic import BeforeValidator, BaseModel, ConfigDict

# Helper to convert MongoDB ObjectId to string
PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
