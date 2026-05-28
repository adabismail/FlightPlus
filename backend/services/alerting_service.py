# Email function uses Django's built-in send_mail():
send_mail(
    subject  = 'Deal Alert: DEL → DXB for ₹12,000',
    message  = body_text,
    from_email     = settings.DEFAULT_FROM_EMAIL,
    recipient_list = [user.email],
)
 
# SMS function uses Twilio's Python SDK:
from twilio.rest import Client
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
client.messages.create(
    body  = '✈ Deal! DEL→DXB ₹12,000 (save ₹6,000!)',
    from_ = settings.TWILIO_FROM_NUMBER,
    to    = user.phone,
)
 
# dispatch_alert() calls both based on user preferences:
def dispatch_alert(user, route, offer):
    report = {'email': False, 'sms': False}
    if user.notify_email:
        report['email'] = send_deal_email(user, route, offer)
    if user.notify_sms:
        report['sms']   = send_deal_sms(user, route, offer)
    return report
