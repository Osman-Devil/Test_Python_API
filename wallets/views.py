import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Wallet
from decimal import Decimal, InvalidOperation

# Настраиваем логирование
logger = logging.getLogger(__name__)

class WalletDetailView(APIView):
    """ Получение информации о кошельке """
    def get(self, request, wallet_uuid):
        wallet = get_object_or_404(Wallet, uuid=wallet_uuid)
        return Response({"uuid": str(wallet.uuid), "balance": str(wallet.balance)})

class WalletOperationView(APIView):
    """ Пополнение и снятие средств с кошелька """
    def post(self, request, wallet_uuid):
        wallet = get_object_or_404(Wallet, uuid=wallet_uuid)
        operation_type = request.data.get("operationType")
        amount = request.data.get("amount")

        # Проверяем, что переданная сумма корректна
        try:
            amount = Decimal(str(amount))  # Преобразование в строку
        except (TypeError, InvalidOperation):
            return Response({"error": "Incorrect amount"}, status=status.HTTP_400_BAD_REQUEST)

        if operation_type == "DEPOSIT":
            wallet.balance += amount
            wallet.save()
            logger.info(f"Пополнение: {wallet.uuid} +{amount}")

        elif operation_type == "WITHDRAW":
            if wallet.balance < amount:
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
            wallet.balance -= amount
            wallet.save()
            logger.info(f"Снятие: {wallet.uuid} -{amount}")

        else:
            return Response({"error": "Invalid operation type"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"uuid": str(wallet.uuid), "balance": str(wallet.balance)})
