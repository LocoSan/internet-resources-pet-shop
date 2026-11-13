from rest_framework import serializers

from .models import Breed, Pet, Species


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ("id", "name")


class BreedSerializer(serializers.ModelSerializer):
    species_name = serializers.CharField(source="species.name", read_only=True)

    class Meta:
        model = Breed
        fields = ("id", "name", "species", "species_name")


class PetSerializer(serializers.ModelSerializer):
    breed_name = serializers.CharField(source="breed.name", read_only=True)
    species_name = serializers.CharField(source="breed.species.name", read_only=True)

    class Meta:
        model = Pet
        fields = (
            "id", "name", "breed", "breed_name", "species_name",
            "age_months", "price", "description",
        )
