from twilio.rest import Client
import os

# 1. Use Environment Variables (The Billionaire Way - Secure)
# Or for now, paste them here but DELETE before sharing screen
account_sid = 'AC213034d47563aa88df51b2475a554fed'
auth_token = 'bc4743acbfa7a9938c4c2ee41d6136c0' # <--- Paste your NEW token here
client = Client(account_sid, auth_token)

# 2. Send a Simple Text (No Templates yet)
message = client.messages.create(
  from_='whatsapp:+14155238886',  # This must be the Twilio Sandbox Number
  body='✅ Hello from Python! Your Paper Mill Bot is active.',
  to='whatsapp:+919098994187'       # This number must have joined the Sandbox
)

print(f"Message Sent! SID: {message.sid}")