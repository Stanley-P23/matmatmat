import smtplib
import os
MY_EMAIL = os.environ.get('MY_EMAIL')
PASSWORD = os.environ.get('PASSWORD')


class NotificationManager:

    def __init__(self, series, addresses):


            self.addresses = addresses
            self.addresses.append(MY_EMAIL)

            self.message_text = f"Udostępniłem kolejną serię zadań - {series.title}.\n" \
                                f"Seria jest dostępna pod " \
                                f"linkiem: " \
                                f"https://matmatmat.pl/tests.\nTermin wykonania zadań mija:" \
                                f" {series.finish_date}."


            self.message_end = "Powodzenia!"

            self.message_greeting = "Dzień dobry,"

            self.message_subject = f"Subject: Nowa seria zadań z matematyki - {series.title}"

    def send_mail(self):


        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()  # message is encrypted
            connection.login(user=MY_EMAIL, password=PASSWORD)
            connection.sendmail(from_addr=MY_EMAIL, to_addrs=self.addresses, msg=(f"{self.message_subject}\n\n"
                                                                           f"{self.message_greeting}\n\n"
                                                                           f"{self.message_text}\n\n"
                                                                           f"{self.message_end}").encode('utf8'))




