from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import (
    DoctorViewSet,
    PatientViewSet,
    ExerciseViewSet,
    PatientExerciseViewSet,
    DoctorExerciseViewSet,
)


router = DefaultRouter()

router.register('doctors', DoctorViewSet)
router.register('patients', PatientViewSet)
router.register('exercises', ExerciseViewSet),
router.register('patient-exercises', PatientExerciseViewSet)
router.register(
    r'patients/(?P<patient_id>\d+)/exercises',
    PatientExerciseViewSet,
    basename='patient-exercises',
)
router.register(
    r'doctors/(?P<doctor_id>\d+)/exercises',
    DoctorExerciseViewSet,
    basename='doctor-exercises',
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
