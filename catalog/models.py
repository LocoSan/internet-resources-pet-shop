from django.core.validators import MinValueValidator
from django.db import models


class Species(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Breed(models.Model):
    name = models.CharField(max_length=80)
    species = models.ForeignKey(Species, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["species", "name"], name="unique_breed_in_species"),
        ]

    def __str__(self):
        return self.name


class Pet(models.Model):
    name = models.CharField(max_length=80)
    breed = models.ForeignKey(Breed, on_delete=models.PROTECT)
    age_months = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(max_length=500, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="pet_price_nonnegative"),
        ]

    def __str__(self):
        return self.name
