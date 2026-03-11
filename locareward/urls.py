from rest_framework.routers import DefaultRouter

from locareward.apps import LocarewardConfig
from locareward.views import (LikeActionViewSet, LocationViewSet,
                              NeedActionViewSet, RewardViewSet)

app_name = LocarewardConfig.name

router = DefaultRouter()
router.register("locations", LocationViewSet, basename="locations")
router.register("likeactions", LikeActionViewSet, basename="likeactions")
router.register("needactions", NeedActionViewSet, basename="needactions")
router.register("rewards", RewardViewSet, basename="rewards")


urlpatterns = [] + router.urls
