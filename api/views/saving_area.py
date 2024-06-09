from rest_framework import generics
from ..models import SavingArea
from ..serializers import SavingAreaSerializer
from rest_framework.filters import OrderingFilter

class SavingAreaListCreateAPIView(generics.ListCreateAPIView):
    queryset = SavingArea.objects.all()
    serializer_class = SavingAreaSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['priority']
    ordering = ['-priority']

class SavingAreaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SavingArea.objects.all()
    serializer_class = SavingAreaSerializer