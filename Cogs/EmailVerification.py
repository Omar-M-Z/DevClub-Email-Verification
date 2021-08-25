from discord.ext import commands
import random
import string
import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

def GetVerificactionCode():
    verificationCode = ""
    for i in range(6):
        if random.randint(1, 2) == 1:
            verificationCode = verificationCode + random.choice(string.ascii_letters)
        else:
            verificationCode = verificationCode + str(random.randint(0, 9))
    return verificationCode

def SendVerificationEmail(address, verificationCode, member):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        emailBodyText = f"Your verification code for the DHS Developer Club Discord server is {verificationCode}. This request was submitted by {member} on Discord. If you are not the submitter of this request, please ignore this email. \n\nThis email account is in no way affiliated with the ISG organization."
        message = MIMEMultipart()
        message['From'] = "Developer Club Verification"
        message['To'] = address
        message['Subject'] = "DHS Developer Club Discord Server Verification"
        message.attach(MIMEText(emailBodyText.format(), "plain"))
        server.sendmail(os.environ.get("EMAIL_USER"), address, message.as_string())
        server.quit()

def CheckEmail(email):
    email_address = email
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': email_address})
    status = response.json()['status']
    if status == "valid":
        return True
    else:
        return False

usersAndAttempts = {}
unverifiedRoleID = 879755217028149258

class NoAttemptsLeft(Exception):
    pass

class EmailVerification(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def VerifyMember(self, member):
        await member.add_roles(member.guild.get_role(unverifiedRoleID))
        message = await member.send("To verify yourself and gain access to the server please enter your school email. You have 3 attempts to enter a valid email.")
        channel = message.channel
        usersAndAttempts[member] = 3
        verifcationCode = GetVerificactionCode()

        entry = None
        def check(entry):
            if entry.content.endswith("isg.edu.sa") and entry.author == member and entry.channel == channel and CheckEmail(entry.content) == True:
                SendVerificationEmail(entry.content, verifcationCode, member)
                return True
            else:
                usersAndAttempts[member] = usersAndAttempts[member] - 1
                if usersAndAttempts[member] < 1:
                    usersAndAttempts.pop(member)
                    raise NoAttemptsLeft
                return False
        try:
            entry = await self.client.wait_for('message', check = check, timeout = 300)
            await member.send("You will be sent an email with a verification code. Please enter your verification code here. You have 3 attempts to enter the correct code.")
            usersAndAttempts[member] = 3
        except asyncio.TimeoutError:
            await member.send("You have ran out of time. Leave and rejoin the server to restart the verification process.")
            usersAndAttempts.pop(member)
            return

        def check(entry):
            if entry.content == verifcationCode and entry.author == member and entry.channel == channel:
                return True
            else:
                usersAndAttempts[member] = usersAndAttempts[member] - 1
                if usersAndAttempts[member] < 1:
                    usersAndAttempts.pop(member)
                    raise NoAttemptsLeft
                return False
        try:
            entry = await self.client.wait_for('message', check = check, timeout = 300)
            await member.send("You have successfully been verified and will gain access to the server.")
            await member.remove_roles(member.guild.get_role(unverifiedRoleID))
            usersAndAttempts.pop(member)
        except asyncio.TimeoutError:
            await member.send("You have ran out of time. Leave and rejoin the server to restart the verification process.")
            usersAndAttempts.pop(member)
            return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            await self.VerifyMember(member)
        except NoAttemptsLeft:
            await member.send("You have ran out of attempts. Leave and rejoin the server to restart the verification process.")

def setup(client):
    client.add_cog(EmailVerification(client))