class PreswaldError(Exception):
    """Base exception for all Preswald errors"""
    pass

class ComponentError(PreswaldError):
    """Base exception for component errors"""
    pass

class ValidationError(ComponentError):
    """Raised when component validation fails"""
    pass

class ServiceError(PreswaldError):
    """Base exception for service errors"""
    pass

class StateError(ServiceError):
    """Raised when there's an issue with component state"""
    pass 