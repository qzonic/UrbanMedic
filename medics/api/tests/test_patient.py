from datetime import timedelta, date, datetime

from django.test import Client
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Patient, Doctor, Exercise, PatientExercise


class TestPatient(APITestCase):
    """ Test patient logic. """

    @classmethod
    def setUpClass(cls):
        super(TestPatient, cls).setUpClass()
        cls.client = Client()

    def setUp(self) -> None:
        self.first_patient = Patient.objects.create(
            first_name='Александр',
            last_name='Сидов'
        )

        self.first_doctor = Doctor.objects.create(
            first_name='Михаил',
            last_name='Фролов'
        )
        self.second_doctor = Doctor.objects.create(
            first_name='Александр',
            last_name='Постольников'
        )
        self.third_doctor = Doctor.objects.create(
            first_name='Анастасия',
            last_name='Лёвкина'
        )

        self.first_exercise = Exercise.objects.create(
            name='Ходьба',
            period=timedelta(days=1)
        )
        self.first_exercise.doctors.add(self.first_doctor)
        self.first_exercise.doctors.add(self.second_doctor)
        self.first_exercise.doctors.add(self.third_doctor)
        self.second_exercise = Exercise.objects.create(
            name='Бег',
            period=timedelta(days=2)
        )
        self.second_exercise.doctors.add(self.second_doctor)
        self.third_exercise = Exercise.objects.create(
            name='Подтягивание',
            period=timedelta(days=3)
        )
        self.third_exercise.doctors.add(self.third_doctor)

        self.first_patient_exercise_1 = PatientExercise.objects.create(
            patient=self.first_patient,
            doctor=self.first_doctor,
            exercise=self.first_exercise,
            date_assigned=date(2023, 8, 2),
        )
        self.first_patient_exercise_2 = PatientExercise.objects.create(
            patient=self.first_patient,
            doctor=self.second_doctor,
            exercise=self.second_exercise,
            date_assigned=date(2023, 8, 2),
        )
        self.first_patient_exercise_3 = PatientExercise.objects.create(
            patient=self.first_patient,
            doctor=self.third_doctor,
            exercise=self.third_exercise,
            date_assigned=date(2023, 8, 2),
        )

    def test_create_patient_with_long_name(self):
        data = {
            'first_name': 'Напу Амо Хала Она Она Анека Вехи Вехи Она Хивеа Нена Вава Кехо Онка Ка',
            'last_name': 'Пабло Диего Хозе Франциско де Паула Хуан Непомукено Криспин Криспиано'
        }
        response = self.client.post('/api/v1/patients/', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.json())
        self.assertIn('last_name', response.json())

        expected_first_name = ['Ensure this field has no more than 64 characters.']
        expected_last_name = ['Ensure this field has no more than 64 characters.']
        self.assertEqual(response.json()['first_name'], expected_first_name)
        self.assertEqual(response.json()['last_name'], expected_last_name)

    def test_create_patient(self):
        patient_exercises_count = Patient.objects.count()
        data = {
            'first_name': 'Маргарита',
            'last_name': 'Рябова'
        }
        response = self.client.post('/api/v1/patients/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            patient_exercises_count + 1,
            Patient.objects.count()
        )
        self.assertEqual(response.json()['first_name'], data['first_name'])
        self.assertEqual(response.json()['last_name'], data['last_name'])

    def test_get_patient_info(self):
        response = self.client.get(f'/api/v1/patients/{self.first_patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()['first_name'], self.first_patient.first_name)
        self.assertEqual(response.json()['last_name'], self.first_patient.last_name)

    def test_get_patient_exercises(self):
        count = PatientExercise.objects.filter(patient=self.first_patient).count()
        response = self.client.get(f'/api/v1/patients/{self.first_patient.id}/exercises/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        expected_keys = ['count', 'next', 'previous', 'results']

        self.assertEqual(response_json['count'], count)
        self.assertEqual(list(response_json.keys()), expected_keys)
        for exercise in response_json['results']:
            self.assertTrue(
                PatientExercise.objects.filter(
                    patient=self.first_patient,
                    doctor__id=exercise['doctor']['id'],
                    exercise__id=exercise['exercise']['id']
                ).exists()
            )

    def test_filter_patient_exercises_by_date(self):
        target_date = date.today() + timedelta(days=1)
        response = self.client.get(f'/api/v1/patients/{self.first_patient.id}/exercises/?date={target_date}')

        response_json = response.json()
        exercise_count = 1
        self.assertEqual(response_json['count'], exercise_count)
        for exercise in response_json['results']:
            self.assertTrue(
                PatientExercise.objects.filter(
                    patient=self.first_patient,
                    doctor__id=exercise['doctor']['id'],
                    exercise__id=exercise['exercise']['id']
                ).exists()
            )

        result = response_json['results'][0]
        period_raw = result['exercise']['period']
        day, time = period_raw.split(' ')
        hours, minutes, seconds = map(int, time.split(":"))

        period = timedelta(days=int(day), hours=hours, minutes=minutes, seconds=seconds)
        date_assigned_raw = datetime.strptime(result['date_assigned'], '%Y-%m-%d')
        date_assigned = date(date_assigned_raw.year, date_assigned_raw.month, date_assigned_raw.day)
        days = (target_date - date_assigned).days
        self.assertTrue(days % period.days == 0)
