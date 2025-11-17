# Python modules
from datetime import timedelta, date


# Django modules
from django.utils.timezone import now
from django.db.models import (
    Q,
    Count,
    Avg,
    Min,
    Max,
    Sum,
    Value,
    When,
    Case,
    CharField,
    ExpressionWrapper,
    F,
    DurationField,
)
from django.db.models.functions import Concat, ExtractYear, Now


from apps.auths.models import CustomUser


# 2.1 Get all active users.

CustomUser.objects.filter(is_active=False)

# 2.2 Get all users whose email ends with @gmail.com.

CustomUser.objects.filter(email__endswith="@gmail.com")

# 2.3 Get all users from the city "Almaty".
CustomUser.objects.filter(city__iexact="Almaty")

# 2.4 Get all users not from the city "Almaty" (use .exclude()).

CustomUser.objects.exclude(city__iexact="Almaty")

# 2.5 Get all users with salary > 500000.

CustomUser.objects.filter(salary__gt=500_000)

# 2.6 Get all users from department "IT" and country "Kazakhstan".

CustomUser.objects.filter(department="IT", country="Kazakhstan")

# 2.7 Get all users where birth_date is NULL (not set).

CustomUser.objects.filter(birth_rate__isnull=True)

# 2.8 Get all users whose first_name starts with "A" (case-insensitive).

CustomUser.objects.filter(first_name__istartswith="A")

# 2.9 Get the total number of users in the system.

CustomUser.objects.count()


# 2.10 Get the first 20 users ordered by date_joined descending.

CustomUser.objects.order_by("-date_joined")[:20]

# 2.11 Get distinct list of cities of all users.

CustomUser.objects.values_list("city", flat=True).distinct()


# 2.12 Count how many users belong to department "Sales".

CustomUser.objects.filter(department="Sales").count()

# 2.13 Get all users who have logged in during the last 7 days.

CustomUser.objects.filter(last_login__gte=now() - timedelta(days=7))

# 2.14 Get all users whose name or surname contains "bek" (use Q + icontains).

CustomUser.objects.filter(
    Q(first_name__icontains="bek") | Q(last_name__icontains="bek")
)


# 2.15 Get all users whose salary is between 300000 and 700000 (inclusive).

CustomUser.objects.filter(salary_range=(300_000, 700_000))

# 2.16 Get all users whose department is in ["IT", "HR", "Finance"].

CustomUser.objects.values("department").annotate(total=Count("id"))


# 2.17 Group users by department and get the number of users per department.

CustomUser.objects.values("department").annotate(total=Count("id"))

# 2.18 Same as above, but order the result by the number of users descending.

CustomUser.objects.values("department").annotate(total=Count("id")).order_by(
    "-total"
)  # noqa

# 2.19 Get top 5 cities with the highest number of users.

CustomUser.objects.values("city").annotate(total=Count("id")).order_by("-total")[
    :5
]  # noqa


# 2.20 Get all users who never logged in (last_login__isnull=True).

CustomUser.objects.filter(last_login__isnull=True)


# 2.21 Get the average salary of all users.

CustomUser.objects.aggregate(Avg_salary=Avg("salary"))

# 2.22 Get the max and min salary among all users.

CustomUser.objects.aggregate(Max_salary=Max("salary"), Min_salary=Min("salary"))

# 2.23 Get all users who have phone numbers containing "+7".

CustomUser.objects.filter(phone__contains="+7")

# 2.24 Annotate each user with a full_name = first_name + " " + last_name.

CustomUser.objects.annotate(full_name=Concat("first_name", Value(" "), "last_name"))

# 2.25 Annotate each user with the birth year (extract year from birth_date) and order by this year.

CustomUser.objects.annotate(birth_year=ExtractYear("birth_date")).order_by("birth_year")

# 2.26 Get all users born in May (birth_date__month=5).

CustomUser.objects.filter(birth_date__month=5)

# 2.27 Get all users with role="manager" and salary greater than 400000.

CustomUser.objects.filter(role="Manager", salary__gt=400_000)

# 2.28 Get all users with role="employee" or department "HR".

CustomUser.objects.filter(Q(role="Employee") | Q(department="HR"))

# 2.29 Count active users in each city (group by city, filter is_active=True).

CustomUser.objects.filter(is_active=True).values("city").annotate(total=Count("id"))

# 2.30 Get the 10 earliest registered users (order by date_joined ascending).

CustomUser.objects.order_by("date_joined")[:10]

# 2.31 Get users whose city starts with "A" and whose salary is greater than 300000.

CustomUser.objects.filter(city__istartswith="A", salary__gt=300_000)

# 2.32 Get all users with an empty or null department (check both isnull and empty string).

CustomUser.objects.filter(Q(department__isnull=True) | Q(departments=""))

# 2.33 Get stats by country: country name, number of users, and average salary per country.

CustomUser.objects.values("country").annotate(total=Count("id"), Avg=Avg("Salary"))

# 2.34 Get all staff users (is_staff=True) ordered by last_login descending.

CustomUser.objects.filter(is_staff=True).order_by("-last_login")

# 2.35 Get all users whose email does not contain "example.com".

CustomUser.objects.exclude(email__icontains="example.com")

# 2.36 Get all users whose salary is higher than the average salary (two-step or subquery — your choice).

AvgSalary = CustomUser.objects.aggregate(Avg=Avg("salary"))["Avg"]
CustomUser.objects.filter(salary__gt=AvgSalary)


# 2.37 Find emails that are used by more than one user (group by email and filter by Count("id") > 1).

CustomUser.objects.values("email").annotate(total=Count("id")).filter(total__gt=1)

# 2.38 Annotate users with a computed field salary_level using Case/When: "low" for salary < 300000 "medium" for 300000–700000 "high" for > 700000 Then order by this annotated field.

CustomUser.objects.annotate(
    salary_level=Case(
        When(salary__lt=300_000, then=Value("low")),
        When(salary__lt=700_000, then=Value("medium")),
        default=Value("high"),
        output_field=CharField(),
    )
)

# 2.39 Get all users whose date_joined is within the current year.

cur_year = date.today().year
CustomUser.objectss.filter(date_joined__year=cur_year)

# 2.40 Get total payroll per department: for each department, sum of salary.

CustomUser.objects.filter("department").annotate(total_payroll=Sum("salary"))

# 2.41 Get all users from "IT" department whose last_login is null — i.e. created but never logged in.

CustomUser.objects.filter(department="IT", last_login__isnull=True)

# 2.42 Get all users whose country="Kazakhstan" but city is null or empty — to find “incomplete” profiles.

CustomUser.objects.filter(country="Kazakhstan").filter(
    Q(city__isnull=True) | Q(city="")
)

# 2.43 Get all users whose birth_date is before 1990-01-01 and salary is not null.
CustomUser.objects.filter(birth_date__lt="1990-01-01", salary__isnull=False)

# 2.44 Get all users and annotate them with years_since_joined (difference between today and date_joined in days/years — students can use ExpressionWrapper with Now()).

CustomUser.objects.annotate(
    years_since_joined=ExpressionWrapper(
        Now() - F("date_joined"), output_field=DurationField
    )
)

# 2.45 Get users whose department is "Sales" and whose email ends with @gmail.com and salary > 350000 (multiple filters).

CustomUser.objects.filter(
    department="Sales", email__iendswith="@gmail.com", salary__gt=300_000
)

# 2.46 Get all users, order them by country, and inside each country — by salary descending (multi-level ordering).

CustomUser.objects.order_by("country", "-salary")

# 2.47 Get the number of users per role (group by role), but show only roles that have more than 100 users.

CustomUser.objects.filter(last_login__lt=F("date_joined"))

# 2.48 Get all users whose last_login is earlier than their date_joined (data inconsistency check).

CustomUser.objects.filter(last_login__lt=F("date_joined"))

# 2.49 Get all users and annotate them with is_senior = True if birth_date is before 1985-01-01, else False.

CustomUser.objects.annotate(
    is_senoir=Case(
        When(birth_date__lt="1985-01-01", then=Value(True)), default=Value(False)
    )
)


# 2.50 Create a query that returns departments sorted by average salary descending, but only for departments that have at least 20 users.

CustomUser.objects.values("department").annotate(
    total=Count("id"), avg_salary=Avg("salary")
).filter(total__gte=20).order_by("-avg_salary")
