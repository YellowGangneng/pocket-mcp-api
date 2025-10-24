"""Enum definitions shared across models and schemas."""

from enum import StrEnum


class RoleEnum(StrEnum):
    MANAGER = "MANAGER"
    USER = "USER"


class StatusEnum(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"
    REVIEW = "REVIEW"
    REJECTED = "REJECTED"
    ACCEPT = "ACCEPT"


class ActivityEnum(StrEnum):
    LOGIN = "LOGIN"
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class TargetEnum(StrEnum):
    USER = "USER"
    MCP_SERVER = "MCP_SERVER"
    AGENT = "AGENT"


class IOEnum(StrEnum):
    IN = "IN"
    OUT = "OUT"


class DeviceEnum(StrEnum):
    PC = "PC"
    MOBILE = "MOBILE"


class PermissionEnum(StrEnum):
    EDIT = "EDIT"
    VIEW = "VIEW"


class VisibilityEnum(StrEnum):
    ALL = "ALL"
    AUTHORIZED = "AUTHORIZED"
    PRIVATE = "PRIVATE"
