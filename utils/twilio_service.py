from twilio.rest import Client
import random
from config import Settings

settings = Settings()



class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID,
                             settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER

    def generate_verification_code(self):
        """Generate a 6-digit verification code"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def send_verification_code(self, phone_number: str, code: str):
        try:
            message = self.client.messages.create(
                body=f"Your BudgetBuddy verification code is: {code}",
                from_=self.from_number,
                to=phone_number
            )
            return True, message.sid
        except Exception as e:
            return False, str(e)
