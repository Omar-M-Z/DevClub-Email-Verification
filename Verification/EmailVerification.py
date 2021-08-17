import discord
from discord.ext import commands
import random
import string
import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def GetVerificactionCode():
    verificationCode = ""
    for i in range(6):
        if random.randint(1, 2) == 1:
            verificationCode = verificationCode + random.choice(string.ascii_letters)
        else:
            verificationCode = verificationCode + str(random.randint(0, 9))
    print(verificationCode)
    return verificationCode

def SendVerificationEmail(address, verificationCode):
    print(address)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        bodyText = f"Your verification code for the DHS Developer Club Discord server is {verificationCode}. If you did not submit a request for this, then please ignore this email."
        message = MIMEMultipart()
        message['From'] = "isg.email.verify@gmail.com"
        message['To'] = address
        message['Subject'] = "DHS Developer Club Verification"
        message.attach(MIMEText(bodyText, "plain"))
        server.sendmail(os.environ.get("EMAIL_USER"), address, message.as_string())
        server.quit()

usersInVerificationProcess = []

class EmailVerification(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        message = await member.send("To verify yourself and gain access to the server please enter your school email.")
        channel = message.channel
        usersInVerificationProcess.append(member)

        entry = None
        def check(entry):
            return entry.content.endswith("isg.edu.sa") and entry.author == member and entry.channel == channel
        try:
            entry = await self.client.wait_for('message', check = check, timeout = 300)
            await member.send("You will be sent an email with a verification code. Please enter your verification code here.")
        except asyncio.TimeoutError:
            await member.send("You have ran out of time.")

        verifcationCode = GetVerificactionCode()
        SendVerificationEmail(entry.content, verifcationCode)
        def check(entry):
            return entry.content == verifcationCode and entry.author == member and entry.channel == channel
        try:
            entry = await self.client.wait_for('message', check = check, timeout = 300)
            await member.send("You have successfully been verified and will gain access to the server.")
            usersInVerificationProcess.remove(member)
        except asyncio.TimeoutError:
            await member.send("You have ran out of time.")

def setup(client):
    client.add_cog(EmailVerification(client))