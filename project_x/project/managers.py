from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group

class CustomUserManager(BaseUserManager):
    def _create_user(self, phone, first_name, last_name, iin, position, is_admin, password):
        user = self.model(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            iin=iin,
            position=position
        )
        if not is_admin:
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.set_unusable_password()
            user.save()
        else:
            user.is_superuser = True
            user.is_staff = True
            user.set_password(password)
            user.save()
        return user

    def create_user(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, None, None, True)

    def create_superuser(self, phone, first_name, last_name, iin, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(phone, first_name, last_name, iin, None, True, password)
