from rest_framework.routers import DefaultRouter

from locareward.apps import LocarewardConfig
from locareward.views import ActionViewSet, LocationViewSet, RewardViewSet
from users.apps import UsersConfig

app_name = LocarewardConfig.name

router = DefaultRouter()
router.register("locations", LocationViewSet, basename="locations")
router.register("actions", ActionViewSet, basename="actions")
router.register("rewards", RewardViewSet, basename="rewards")


urlpatterns = [] + router.urls
