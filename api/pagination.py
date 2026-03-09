from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    """
    Paginación personalizada para productos.
    Permite al cliente especificar el tamaño de página via ?page_size=10/25/50/100
    """
    page_size = 10  # Por defecto
    page_size_query_param = 'page_size'
    page_size_query_description = 'Número de resultados por página'
    max_page_size = 100
    page_query_param = 'page'
    page_query_description = 'Número de página a devolver'


class SalesPagination(PageNumberPagination):
    """
    Paginación personalizada para historial de ventas.
    Permite al cliente especificar el tamaño de página via ?page_size=10/25/50
    """
    page_size = 10  # Por defecto - mostrar 10 sales por página
    page_size_query_param = 'page_size'
    page_size_query_description = 'Número de ventas por página'
    max_page_size = 50  # Máximo 50 por página
    page_query_param = 'page'
    page_query_description = 'Número de página a devolver'
