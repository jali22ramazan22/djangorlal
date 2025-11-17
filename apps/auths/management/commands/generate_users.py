# Python modules
from typing import Any
from faker import Faker
from random import randint, choice

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password


# Project modules
from apps.auths.models import CustomUser


_BATCH_SIZE = 1000
_TOTAL_USERS = 10_000


class Command(BaseCommand):

    help = "To generate 10,000 mock users"

    def handle(self, *args: Any, **options: Any) -> None:
        fake = Faker()

        departments = [d[0] for d in CustomUser.DEPARTMENT_CHOICES]
        roles = [r[0] for r in CustomUser.ROLES_CHOICES]

        hashed_password = make_password("12345  ")

        user_batch = []
        created = 0

        for _ in range(_TOTAL_USERS):
            first = fake.first_name()
            last = fake.last_name()

            username = f"{first.lower()}.{last.lower()}{randint(100, 9999999)}"

            user = CustomUser(
                email=f"{username}@{fake.free_email_domain()}",
                username=username,
                first_name=first,
                last_name=last,
                phone=fake.phone_number(),
                city=fake.city(),
                country=fake.country(),
                department=choice(departments),
                role=choice(roles),
                birth_date=fake.date_of_birth(minimum_age=19, maximum_age=50),
                salary=randint(50_000, 2_500_000),
                password=hashed_password,
            )

            user_batch.append(user)

            if len(user_batch) >= _BATCH_SIZE:
                CustomUser.objects.bulk_create(user_batch)
                created += len(user_batch)
                user_batch.clear()
                self.stdout.write(f"Created {created}/{_TOTAL_USERS}")
        if user_batch:
            CustomUser.objects.bulk_create(user_batch)
            created += len(user_batch)

        self.stdout.write(self.style.SUCCESS(f"Done. Total created: {created}"))
