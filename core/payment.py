import requests
from django.conf import settings

class Paystack:
    def __init__(self):
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.initialize_payment_url = "https://api.paystack.co/transaction/initialize"
        self.verify_payment_url = "https://api.paystack.co/transaction/verify/{}"
        self.verify_account_url = "https://api.paystack.co/transferrecipient"
        self.banks_url = "https://api.paystack.co/bank?currency=NGN"
        self.headers = {
            'Authorization': f"Bearer {self.secret_key}"
        }
    
    def initalize_payment(self,email,amount,success_url,ref=None,):
        payload = {
            'email':email,
            'amount': int(amount) * 100,
            'callback_url': success_url,

        }
        if ref:
            payload['reference'] = ref
        
        request = requests.post(self.initialize_payment_url,data=payload,headers=self.headers)
        return request.json()
    def verify_payment(self,ref):
        url = self.verify_payment_url.format(ref)
        request = requests.get(url, headers=self.headers)
        return request.json()
    def make_transfer(self,acc_no,bank_code,amount):
        pass