import requests
from datetime import datetime as dt
import smtplib
import time

try:
    from config import FROM_EMAIL, PW, TO_EMAIL, MY_LAT, MY_LONG
except ModuleNotFoundError:
    from config_dummy import FROM_EMAIL, PW, TO_EMAIL, MY_LAT, MY_LONG


def iss_locator():
    """Locates the ISS and returns whether it is within 5 degrees of the specified location, and also returns the
    coordinates of the ISS at the time of the reading."""
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    if ((iss_latitude - MY_LAT) ** 2 + (iss_longitude - MY_LONG) ** 2) ** 0.5 <= 5:
        return True, (iss_latitude, iss_longitude)  # Your position is within 5 degrees of the ISS. Pythagorean style.
    else:
        return False, (None, None)


def is_night():
    """Determines whether current hour is between the sunset hour and sunrise hour to see if it's dark enough to see the
     ISS. Returns boolean."""
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()

    data = response.json()
    sunrise_utc = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset_utc = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    utc_now = dt.utcnow().hour

    if utc_now >= sunset_utc or utc_now <= sunrise_utc:
        return True  # It's dark


while True:
    time.sleep(60)
    iss_overhead, iss_location = iss_locator()
    if iss_overhead and is_night():
        cnxn = smtplib.SMTP("smtp.gmail.com", 587, timeout=120)
        cnxn.starttls()
        cnxn.login(user=FROM_EMAIL, password=PW)
        cnxn.sendmail(
            from_addr=FROM_EMAIL,
            to_addrs=TO_EMAIL,
            msg=f"Subject:Look Up!\n\nThe ISS is currently above you at {iss_location}! "
                f"Put your glasses on and go check it out!"
        )
        time.sleep(240)
