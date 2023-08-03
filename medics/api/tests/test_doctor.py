from datetime import timedelta, date

from django.test import Client
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Patient, Doctor, Exercise, PatientExercise


class TestDoctor(APITestCase):
    """ Test doctor logic. """

    @classmethod
    def setUpClass(cls):
        super(TestDoctor, cls).setUpClass()
        cls.client = Client()

    def setUp(self) -> None:
        self.first_patient = Patient.objects.create(
            first_name='Александр',
            last_name='Сидов'
        )
        self.second_patient = Patient.objects.create(
            first_name='Дмитрий',
            last_name='Копылов'
        )
        self.third_patient = Patient.objects.create(
            first_name='Константин',
            last_name='Грибоедов'
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

        self.first_patient_exercise = PatientExercise.objects.create(
            patient=self.first_patient,
            doctor=self.first_doctor,
            exercise=self.first_exercise,
        )
        self.second_patient_exercise = PatientExercise.objects.create(
            patient=self.second_patient,
            doctor=self.first_doctor,
            exercise=self.first_exercise,
        )
        self.third_patient_exercise = PatientExercise.objects.create(
            patient=self.third_patient,
            doctor=self.second_doctor,
            exercise=self.second_exercise,
        )

    def test_create_doctor_with_long_name(self):
        data = {
            'first_name': 'Напу Амо Хала Она Она Анека Вехи Вехи Она Хивеа Нена Вава Кехо Онка Ка',
            'last_name': 'Пабло Диего Хозе Франциско де Паула Хуан Непомукено Криспин Криспиано'
        }
        response = self.client.post('/api/v1/doctors/', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.json())
        self.assertIn('last_name', response.json())

        expected_first_name = ['Ensure this field has no more than 64 characters.']
        expected_last_name = ['Ensure this field has no more than 64 characters.']
        self.assertEqual(response.json()['first_name'], expected_first_name)
        self.assertEqual(response.json()['last_name'], expected_last_name)

    def test_create_doctor(self):
        doctor_exercises_count = Doctor.objects.count()
        data = {
            'first_name': 'Юрий',
            'last_name': 'Илюхин'
        }
        response = self.client.post('/api/v1/doctors/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            doctor_exercises_count + 1,
            Doctor.objects.count()
        )
        self.assertEqual(response.json()['first_name'], data['first_name'])
        self.assertEqual(response.json()['last_name'], data['last_name'])

    def test_get_doctor_info(self):
        response = self.client.get(f'/api/v1/doctors/{self.first_doctor.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()['first_name'], self.first_doctor.first_name)
        self.assertEqual(response.json()['last_name'], self.first_doctor.last_name)

    def test_get_doctor_exercises(self):
        count = PatientExercise.objects.filter(doctor=self.first_doctor).count()
        response = self.client.get(f'/api/v1/doctors/{self.first_doctor.id}/exercises/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        expected_keys = ['count', 'next', 'previous', 'results']

        self.assertEqual(response_json['count'], count)
        self.assertEqual(list(response_json.keys()), expected_keys)
        for exercise in response_json['results']:
            self.assertTrue(
                PatientExercise.objects.filter(
                    patient__id=exercise['patient']['id'],
                    doctor=self.first_doctor,
                    exercise__id=exercise['exercise']['id']
                ).exists()
            )

    def test_create_patient_exercise_by_bad_doctor(self):
        doctor_exercises_count = PatientExercise.objects.count()
        data = {
            'patient': self.first_patient.id,
            'exercise': self.second_exercise.id
        }
        response = self.client.post(f'/api/v1/doctors/{self.first_doctor.id}/exercises/', data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            doctor_exercises_count,
            PatientExercise.objects.count()
        )
        error = response.json()['doctor']
        massage = 'Этот доктор не может назначить это упражнение!'
        self.assertIn(massage, error)

    def test_create_existing_patient_exercise(self):
        doctor_exercises_count = PatientExercise.objects.count()
        data = {
            'patient': self.first_patient.id,
            'exercise': self.first_exercise.id
        }
        response = self.client.post(f'/api/v1/doctors/{self.first_doctor.id}/exercises/', data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            doctor_exercises_count,
            PatientExercise.objects.count()
        )
        error = response.json()['patient']
        massage = 'Этому пациенту уже назначили это упражнение!'
        self.assertIn(massage, error)

    def test_create_patient_exercise(self):
        doctor_exercises_count = PatientExercise.objects.count()
        data = {
            'patient': self.third_patient.id,
            'exercise': self.first_exercise.id
        }
        response = self.client.post(f'/api/v1/doctors/{self.first_doctor.id}/exercises/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            doctor_exercises_count + 1,
            PatientExercise.objects.count()
        )

    def test_filter_exercises_by_doctor_id(self):
        response = self.client.get(f'/api/v1/exercises/?doctors__id={self.first_doctor.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        count = 1
        expected_keys = ['count', 'next', 'previous', 'results']

        self.assertEqual(response_json['count'], count)
        self.assertEqual(list(response_json.keys()), expected_keys)
        for exercise in response_json['results']:
            period_raw = exercise['period']
            day, time = period_raw.split(' ')
            hours, minutes, seconds = map(int, time.split(":"))

            period = timedelta(days=int(day), hours=hours, minutes=minutes, seconds=seconds)
            self.assertTrue(
                Exercise.objects.filter(
                    name=exercise['name'],
                    period=period,
                    doctors__id=self.first_doctor.id
                ).exists()
            )



