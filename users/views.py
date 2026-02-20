from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from rest_framework.viewsets import ModelViewSet
from users.models import User
from users.serializers import UserRoleUpdateSerializer

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')

        if not amount:
            return Response(
                {'detail': 'Amount is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = Decimal(amount)
        except:
            return Response(
                {'detail': 'Invalid amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount <= 0:
            return Response(
                {'detail': 'Deposit must be positive.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        user.balance += amount
        user.save()

        return Response({
            'message': 'Deposit successful',
            'new_balance': user.balance
        })
    
class UserRoleManagementViewSet(ModelViewSet):
    '''
    Only Admin can change the role of the user as 
    -Custmer
    -Seller
    -Admin
    method: PATCH 
    endpoint: /api/v1/admin/users/{id}/
    value for example:
        {
            "role": "seller"
        }
    '''
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['patch']