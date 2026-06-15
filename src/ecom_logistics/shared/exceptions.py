from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationError:
    entity_id: str
    field: str
    message: str


class DomainError(Exception):
    pass


class DomainValidationError(DomainError):
    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        super().__init__(str([e.message for e in errors]))

class BusinessRuleViolation(DomainError):
    pass

class ApplicationError(Exception):
    pass

class NotFoundError(ApplicationError):
    pass

class ConflictError(ApplicationError):
    pass

class PermissionDeniedError(ApplicationError):
    pass

class InfrastructureError(Exception):
    pass