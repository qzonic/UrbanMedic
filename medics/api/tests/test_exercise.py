from datetime import timedelta

from django.test import Client
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Patient, Doctor, Exercise, PatientExercise


class TestExercise(APITestCase):
    """ Test exercise logic. """

    @classmethod
    def setUpClass(cls):
        super(TestExercise, cls).setUpClass()
        cls.client = Client()

    def setUp(self) -> None:
        self.first_doctor = Doctor.objects.create(
            first_name='Павел',
            last_name='Глызин'
        )
        self.second_doctor = Doctor.objects.create(
            first_name='Федор',
            last_name='Короткий'
        )

        self.patient = Patient.objects.create(
            first_name='Django',
            last_name='Python'
        )

    def test_create_exercise(self):
        data = {
            'name': 'Плавание',
            'period': '5 00:00:00',
            'doctors': [
                self.first_doctor.id,
                self.second_doctor.id
            ]
        }
        response = self.client.post('/api/v1/exercises/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Exercise.objects.filter(
            name=data['name'],
            period=timedelta(days=5)
        ).exists())


