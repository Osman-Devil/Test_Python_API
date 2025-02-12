from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from wallets.models import Wallet
from decimal import Decimal

class WalletAPITest(APITestCase):
    """Тесты API для кошельков"""

    def setUp(self):
        """Создаём тестовый кошелёк перед каждым тестом"""
        self.wallet = Wallet.objects.create(balance=Decimal("0.00"))
        self.wallet_url = reverse('wallet-detail', kwargs={'wallet_uuid': self.wallet.uuid})
        self.operation_url = reverse('wallet-operation', kwargs={'wallet_uuid': self.wallet.uuid})

    def test_get_wallet_info(self):
        """Тест получения информации о кошельке"""
        response = self.client.get(self.wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], str(self.wallet.uuid))
        self.assertEqual(str(response.data['balance']), "0.00")

    def test_deposit_money(self):
        """Тест пополнения кошелька"""
        data = {"operationType": "DEPOSIT", "amount": "100.00"}  # Используем строку
        response = self.client.post(self.operation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(str(self.wallet.balance), "100.00")

    def test_withdraw_money_success(self):
        """Тест успешного снятия денег"""
        self.wallet.balance = Decimal("200.00")
        self.wallet.save()
        data = {"operationType": "WITHDRAW", "amount": "50.00"}  # Используем строку
        response = self.client.post(self.operation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(str(self.wallet.balance), "150.00")

    def test_withdraw_money_fail(self):
        """Тест снятия денег при недостаточном балансе"""
        data = {"operationType": "WITHDRAW", "amount": "100.00"}  # Используем строку
        response = self.client.post(self.operation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Insufficient funds")

    def test_invalid_operation_type(self):
        """Тест запроса с некорректным типом операции"""
        data = {"operationType": "INVALID", "amount": "50.00"}  # Используем строку
        response = self.client.post(self.operation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid operation type")
