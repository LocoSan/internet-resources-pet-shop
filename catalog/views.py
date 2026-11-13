from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from .models import Breed, Pet, Species
from .serializers import BreedSerializer, PetSerializer, SpeciesSerializer


class CatalogViewSet(ModelViewSet):
    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as error:
            raise ValidationError({"detail": "Сначала удалите или измените связанные записи."}) from error


class SpeciesViewSet(CatalogViewSet):
    queryset = Species.objects.order_by("id")
    serializer_class = SpeciesSerializer


class BreedViewSet(CatalogViewSet):
    queryset = Breed.objects.select_related("species").order_by("id")
    serializer_class = BreedSerializer


class PetViewSet(CatalogViewSet):
    queryset = Pet.objects.select_related("breed__species").order_by("id")
    serializer_class = PetSerializer
