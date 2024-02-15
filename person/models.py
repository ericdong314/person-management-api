from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class Person(AbstractUser):
    # AbstractUser has fields [username, password, first_name, last_name, email, is_staff(admin)]
    
    date_of_birth = models.DateField(blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r"^\+?\d{8,15}$",
        message="Phone number format: '(+)ccxxxxxxxxxx' with 8 to 15 digits.",
    )
    phone = models.CharField(blank=True, validators=[phone_regex], max_length=16)

    # Age is not stored but calculated from date_of_birth
    def get_age(self):
        birth = self.date_of_birth
        if not birth:
            return None
        now = timezone.now()
        birthday_passed = (now.month, now.day) >= (birth.month, birth.day)
        age = now.year - birth.year
        if not birthday_passed:
            age -= 1
        return age

    class Meta:
        ordering = ['id']
