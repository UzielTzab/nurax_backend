"""
Excepciones personalizadas centralizadas para la API.
"""
from rest_framework.exceptions import APIException


class InsufficientStockError(APIException):
    """Stock insuficiente para realizar la operación."""
    status_code = 400
    default_detail = "Stock insuficiente"
    default_code = 'insufficient_stock'


class InvalidTransactionError(APIException):
    """Transacción inválida."""
    status_code = 422
    default_detail = "Transacción inválida"
    default_code = 'invalid_transaction'


class UserNotAuthenticatedError(APIException):
    """Usuario no autenticado."""
    status_code = 401
    default_detail = "Usuario no autenticado"
    default_code = 'user_not_authenticated'


class PermissionDeniedError(APIException):
    """Permiso denegado."""
    status_code = 403
    default_detail = "Permiso denegado"
    default_code = 'permission_denied'


class ResourceNotFoundError(APIException):
    """Recurso no encontrado."""
    status_code = 404
    default_detail = "Recurso no encontrado"
    default_code = 'resource_not_found'


class ValidationError(APIException):
    """Error de validación."""
    status_code = 422
    default_detail = "Error de validación"
    default_code = 'validation_error'
