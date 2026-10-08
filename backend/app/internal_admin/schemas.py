from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


class CommandInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: Annotated[int, Field(strict=True, ge=0)]
    reason: str = Field(min_length=5, max_length=500)

    @field_validator("reason", mode="before")
    @classmethod
    def trim(cls, value):
        return value.strip() if isinstance(value, str) else value


class AccountStatusCommand(CommandInput):
    is_active: StrictBool


class JobModerationCommand(CommandInput):
    moderation_status: Literal["allowed", "blocked"]
