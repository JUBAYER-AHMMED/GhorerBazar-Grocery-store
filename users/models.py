from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager
# Create your models here.
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null = True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    CUSTOMER = 'customer'
    SELLER = 'seller'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (SELLER, 'Seller'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CUSTOMER
    )
    # email instead of username
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    def __str__(self):
        return self.email

    @property
    def is_seller(self):
        return self.role == self.SELLER

    @property
    def is_customer(self):
        return self.role == self.CUSTOMER
    