from flask import Flask, render_template, request
from datetime import datetime
import math, json
import pytz
from astro_utils import (
    get_location_by_name,
    get_timezone_name,
    day_number,
    solar_declination,
    compute_all_yantras
)

app = Flask(__name__)

def parse_time_to_hours(time_str):
    """Accept HH:MM or decimal hours"""
    time_str = time_str.strip()
    if ":" in time_str:
        h, m = map(int, time_str.split(":"))
        return h + m / 60.0
    return float(time_str)

def compute_local_solar_time(lat, lon, day, local_clock_hours, tz_name):
    """Compute LST and sunrise/sunset"""
    # UTC offset
    offset_hours = None
    try:
        if tz_name.startswith(("+", "-")):
            offset_hours = float(tz_name)
        else:
            tz = pytz.timezone(tz_name)
            naive_dt = datetime.strptime(f"{datetime.today().strftime('%Y-%m-%d')} {int(local_clock_hours):02d}:00", "%Y-%m-%d %H:%M")
            local_dt = tz.localize(naive_dt)
            offset_hours = local_dt.utcoffset().total_seconds() / 3600.0
    except:
        offset_hours = 0

    # Equation of Time and LSTM
    B = math.radians((360/365)*(day-81))
    eot = 9.87*math.sin(2*B) - 7.53*math.cos(B) - 1.5*math.sin(B)
    LSTM = 15 * offset_hours
    TC_min = 4 * (lon - LSTM) + eot
    LST_hours = local_clock_hours + TC_min / 60.0

    # Sunrise/Sunset
    phi = math.radians(lat)
    delta = math.radians(solar_declination(day))
    sunrise_local = sunset_local = None
    try:
        H0_rad = math.acos(-math.tan(phi) * math.tan(delta))
        H0_deg = math.degrees(H0_rad)
        sunrise_LST = 12 - H0_deg/15
        sunset_LST = 12 + H0_deg/15
        sunrise_local = sunrise_LST - TC_min/60
        sunset_local = sunset_LST - TC_min/60
        def hours_to_hm(hours):
            h = int(hours)
            m = int((hours - h) * 60)
            return f"{h:02d}:{m:02d}"
        sunrise_local = hours_to_hm(sunrise_local)
        sunset_local = hours_to_hm(sunset_local)
    except ValueError:
        sunrise_local = sunset_local = "Sun does not rise/set"

    return LST_hours, sunrise_local, sunset_local, offset_hours, eot, LSTM, TC_min

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error_msg = None
    sunrise_local = sunset_local = None
    extra_info = {}

    if request.method == "POST":
        location_name = request.form.get("location")
        date_str = request.form.get("date")
        time_input = request.form.get("time")
        country_pref = request.form.get("country_pref")  # Y/N for India

        # 1️⃣ Get location
        if location_name:
            if country_pref == "y":
                location_name += ", India"
            else:
                country_name = request.form.get("country_name")
                if country_name:
                    location_name += f", {country_name}"
            location = get_location_by_name(location_name)
            if location:
                lat, lon = location.latitude, location.longitude
            else:
                lat = lon = None
                error_msg = "Could not determine location. Please enter a valid city."
        else:
            try:
                lat = float(request.form.get("latitude"))
                lon = float(request.form.get("longitude"))
            except:
                error_msg = "Invalid latitude/longitude."

        # 2️⃣ Validate date
        try:
            day = day_number(date_str)
        except Exception as e:
            error_msg = f"Invalid date: {e}"

        # 3️⃣ Parse time
        try:
            local_clock_hours = parse_time_to_hours(time_input)
        except Exception as e:
            error_msg = f"Invalid time input: {e}"

        # 4️⃣ Determine timezone
        tz_name = get_timezone_name(lat, lon) or "UTC"

        if not error_msg:
            # 5️⃣ Compute LST, sunrise, sunset
            t_solar, sunrise_local, sunset_local, offset_hours, eot_min, LSTM, TC_min = compute_local_solar_time(
                lat, lon, day, local_clock_hours, tz_name
            )
            # 6️⃣ Compute yantras
            decl = solar_declination(day)
            results = compute_all_yantras(lat, decl, t_solar)
            extra_info = {
                "LST_hours": round(t_solar, 4),
                "UTC_offset": offset_hours,
                "Equation_of_Time": round(eot_min, 2),
                "LSTM": round(LSTM, 3),
                "Time_Correction": round(TC_min, 2)
            }

    return render_template(
        "index.html",
        results=results,
        error=error_msg,
        sunrise_local=sunrise_local,
        sunset_local=sunset_local,
        extra_info=extra_info
    )

if __name__ == "__main__":
    app.run(debug=True)
