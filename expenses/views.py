"""
Vistas para la app Expenses.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Expense, CashShift
from .serializers import ExpenseSerializer, CashShiftSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet para gastos."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer
    filterset_fields = ['category']
    ordering_fields = ['date']
    ordering = ['-date']
    
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CashShiftViewSet(viewsets.ModelViewSet):
    """ViewSet para turnos de caja."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CashShiftSerializer
    
    def get_queryset(self):
        return CashShift.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Turno abierto actual."""
        shift = CashShift.objects.filter(user=request.user).open().first()
        if shift:
            serializer = self.get_serializer(shift)
            return Response(serializer.data)
        return Response({'detail': 'No hay turno abierto'}, status=404)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
