from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from catalog.views import BreedViewSet, PetViewSet, SpeciesViewSet


router = SimpleRouter()
router.register("species", SpeciesViewSet)
router.register("breeds", BreedViewSet)
router.register("pets", PetViewSet)

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="swagger")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/", include(router.urls)),
]
