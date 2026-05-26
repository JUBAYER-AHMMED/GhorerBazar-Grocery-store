from rest_framework.throttling import UserRateThrottle

class DepositRateThrottle(UserRateThrottle):
    scope = 'deposit'

class ProfileRateThrottle(UserRateThrottle):
    scope = 'profile'

class LoginRateThrottle(UserRateThrottle):
    scope = 'login'