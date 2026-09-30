from __future__ import annotations

from enum import StrEnum


class Provider(StrEnum):
    AZURE = "azure"
    ENTRA = "entra"
    AWS = "aws"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def rank(self) -> int:
        """Higher is worse. Used for sorting."""
        return {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}[self.value]

    @property
    def label(self) -> str:
        return self.value.capitalize()


class Domain(StrEnum):
    IDENTITY = "identity"
    NETWORK = "network"
    DATA = "data"
    LOGGING = "logging"
    RECOVERY = "recovery"
    SECRETS = "secrets"

    @property
    def label(self) -> str:
        return self.value.capitalize()


class Effort(StrEnum):
    S = "S"
    M = "M"
    L = "L"


class Status(StrEnum):
    OPEN = "open"
    ACCEPTED_RISK = "accepted_risk"
    FALSE_POSITIVE = "false_positive"

    @property
    def label(self) -> str:
        return {"open": "Open", "accepted_risk": "Accepted risk", "false_positive": "False positive"}[self.value]


class GapReason(StrEnum):
    MISSING_PERMISSION = "missing_permission"
    AUTH_FAILED = "auth_failed"
    UNSUPPORTED = "unsupported_service"
    ERROR = "error"

    @property
    def label(self) -> str:
        return {
            "missing_permission": "Missing permission",
            "auth_failed": "Authentication failed",
            "unsupported_service": "Unsupported service",
            "error": "Collection error",
        }[self.value]
