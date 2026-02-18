from django.urls import include, path
from habits.apps import HabitsConfig
from habits.views import HabitUsefulRetrieveAPIView, HabitUsefulCreateAPIView, HabitUsefulUpdateAPIView, \
    HabitUsefulDestroyAPIView, HabitUsefulListAPIView, HabitNiceCreateAPIView, HabitNiceRetrieveAPIView, \
    HabitNiceUpdateAPIView, HabitNiceDestroyAPIView, HabitNiceListAPIView, HabitUsefulPublicListAPIView

app_name = HabitsConfig.name

urlpatterns = [
    path('habituseful/create/', HabitUsefulCreateAPIView.as_view(), name='habituseful-create'),
    path('habituseful/<int:pk>/', HabitUsefulRetrieveAPIView.as_view(), name='habituseful-retrieve'),
    path('habituseful/update/<int:pk>/', HabitUsefulUpdateAPIView.as_view(), name='habituseful-update'),
    path('habituseful/delete/<int:pk>/', HabitUsefulDestroyAPIView.as_view(), name='habituseful-destroy'),
    path('habitusefuls/', HabitUsefulListAPIView.as_view(), name='habituseful-list'),
    path('habitusefuls/public/', HabitUsefulPublicListAPIView.as_view(), name='habituseful-list-public'),

    path('habitnice/create/', HabitNiceCreateAPIView.as_view(), name='habitnice-create'),
    path('habitnice/<int:pk>/', HabitNiceRetrieveAPIView.as_view(), name='habitnice-retrieve'),
    path('habitnice/update/<int:pk>/', HabitNiceUpdateAPIView.as_view(), name='habitnice-update'),
    path('habitnice/delete/<int:pk>/', HabitNiceDestroyAPIView.as_view(), name='habitnice-destroy'),
    path('habitnices/', HabitNiceListAPIView.as_view(), name='habitnice-list'),

]


