import smtplib

EMAIL_ADDRESS = "akram2026m@gmail.com"

EMAIL_PASSWORD = "PASTE_NEW_APP_PASSWORD_HERE"


try:

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    server.sendmail(
        EMAIL_ADDRESS,
        EMAIL_ADDRESS,
        "Subject: Test Email\n\nEmail Working Successfully"
    )

    server.quit()

    print("Email Sent Successfully")


except Exception as e:

    print("ERROR IS:")
    print(e)