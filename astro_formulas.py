import math
import json
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from timezonefinder import TimezoneFinder
import pytz

# ----------------- Utility Functions -----------------
def day_number(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.timetuple().tm_yday

def solar_declination(day_of_year):
    # δ = 23.45 * sin((360/365) * (284 + N))
    return 23.45 * math.sin(math.radians((360/365)*(284+day_of_year)))

def deg2rad(deg):
    return deg * math.pi / 180

def rad2deg(rad):
    return rad * 180 / math.pi

def hour_angle(t_solar):
    return 15 * (t_solar - 12)

def altitude(lat, decl, H_deg):
    phi = deg2rad(lat)
    delta = deg2rad(decl)
    H = deg2rad(H_deg)
    sin_alpha = math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta)*math.cos(H)
    alpha = math.asin(max(-1.0, min(1.0, sin_alpha)))
    return rad2deg(alpha)

def shadow_length(height, solar_altitude_deg):
    if solar_altitude_deg <= 0:
        return None
    return round(height / math.tan(deg2rad(solar_altitude_deg)), 2)

# Equation of Time approximation (minutes)
def equation_of_time(day_of_year):
    B = math.radians((360/365) * (day_of_year - 81))  # degrees -> rad
    eot = 9.87 * math.sin(2*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    return eot  # minutes

# ----------------- Yantra Calculators (unchanged) -----------------
def samrat_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    gnomon_height = 10
    return {
        "instrument":"Samrat Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(gnomon_height, alpha),
        "gnomon_height": gnomon_height
    }

def jai_prakash_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    base_radius = 12
    return {
        "instrument":"Jai Prakash Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(base_radius, alpha),
        "base_radius": base_radius
    }

def rama_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    vertical_radius = 10
    return {
        "instrument":"Rama Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(vertical_radius, alpha),
        "vertical_radius": vertical_radius
    }

def digamsa_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    gnomon_height = 8
    return {
        "instrument":"Digamsa Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(gnomon_height, alpha),
        "gnomon_height": gnomon_height
    }

def dhruva_protha_chakra_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    radius = 15
    return {
        "instrument":"Dhruva-Protha-Chakra Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(radius, alpha),
        "radius": radius
    }

def yantra_samrat(lat, decl, t_solar):
    return {
        "instrument":"Yantra-Samrat",
        "Samrat": samrat_yantra(lat, decl, t_solar),
        "DhruvaProthaChakra": dhruva_protha_chakra_yantra(lat, decl, t_solar)
    }

def golayantra_chakra_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    radius = 14
    return {
        "instrument":"Golayantra Chakra Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(radius, alpha),
        "radius": radius
    }

def bhitti_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    height = 8
    return {
        "instrument":"Bhitti Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(height, alpha),
        "height": height
    }

def dakshinottara_bhitti_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    height = 9
    return {
        "instrument":"Dakshinottara Bhitti Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(height, alpha),
        "height": height
    }

def rasivalaya_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    radius = 16
    return {
        "instrument":"Rasivalaya Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(radius, alpha),
        "radius": radius
    }

def nadi_valaya_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    radius = 13
    return {
        "instrument":"Nadi Valaya Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(radius, alpha),
        "radius": radius
    }

def palaka_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    height = 12
    width = 7
    return {
        "instrument":"Palaka Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(height, alpha),
        "height": height,
        "width": width
    }

def chaapa_yantra(lat, decl, t_solar):
    H = hour_angle(t_solar)
    alpha = altitude(lat, decl, H)
    length = 14
    return {
        "instrument":"Chaapa Yantra",
        "solar_altitude_deg": round(alpha,2),
        "hour_angle_deg": round(H,2),
        "shadow_length": shadow_length(length, alpha),
        "length": length
    }

# ----------------- Compute All -----------------
def compute_all_yantras(lat, decl, t_solar):
    return {
        "Samrat": samrat_yantra(lat, decl, t_solar),
        "JaiPrakash": jai_prakash_yantra(lat, decl, t_solar),
        "Rama": rama_yantra(lat, decl, t_solar),
        "Digamsa": digamsa_yantra(lat, decl, t_solar),
        "DhruvaProthaChakra": dhruva_protha_chakra_yantra(lat, decl, t_solar),
        "YantraSamrat": yantra_samrat(lat, decl, t_solar),
        "GolayantraChakra": golayantra_chakra_yantra(lat, decl, t_solar),
        "Bhitti": bhitti_yantra(lat, decl, t_solar),
        "DakshinottaraBhitti": dakshinottara_bhitti_yantra(lat, decl, t_solar),
        "Rasivalaya": rasivalaya_yantra(lat, decl, t_solar),
        "NadiValaya": nadi_valaya_yantra(lat, decl, t_solar),
        "Palaka": palaka_yantra(lat, decl, t_solar),
        "Chaapa": chaapa_yantra(lat, decl, t_solar)
    }

# ----------------- Helpers: location & timezone -----------------
def get_location_by_name(name, retries=2):
    geolocator = Nominatim(user_agent="yantra_app")
    try:
        return geolocator.geocode(name, timeout=10)
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None

def get_timezone_name(lat, lon):
    tf = TimezoneFinder()
    return tf.timezone_at(lat=lat, lng=lon)

def parse_time_to_hours(time_str):
    # Accept "HH:MM" or "H" or decimal "12.5"
    time_str = time_str.strip()
    if ":" in time_str:
        h, m = time_str.split(":")
        return int(h) + int(m)/60.0
    try:
        return float(time_str)
    except:
        raise ValueError("Time must be HH:MM or decimal hours (e.g., 13.5)")

# ----------------- Main Flow (with timezone -> solar time) -----------------
if __name__ == "__main__":
    # 1) get location
    lat = lon = None
    while True:
        location_name = input("Enter location (city/town) or press Enter to input coordinates manually: ").strip()
        if location_name:
            pref_india = input("Do you want to search in India? (Y/N): ").strip().lower()
            if pref_india == "y":
                location_name += ", India"
            else:
                country_name = input("Enter the country name: ").strip()
                location_name += f", {country_name}"

            location = get_location_by_name(location_name)
            if location:
                lat, lon = location.latitude, location.longitude
                print(f"✅ Found location: {location.address}")
                break
            else:
                print("⚠️ Could not fetch location automatically. Try again.")
        else:
            # ask user for coordinates
            while True:
                try:
                    lat = float(input("Enter latitude (degrees): "))
                    lon = float(input("Enter longitude (degrees): "))
                    break
                except ValueError:
                    print("⚠️ Invalid number. Please enter numeric latitude and longitude.")
            break

    print(f"Using -> Latitude: {lat}, Longitude: {lon}")

    # 2) get date with full validation
    while True:
        date_str = input("Enter date (YYYY-MM-DD): ").strip()
        try:
            # validate correct date
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day = day_number(date_str)  # keep your existing day_number calculation
            break
        except ValueError:
            print("⚠️ Invalid date. Please enter a valid date in YYYY-MM-DD format.")

    # 3) determine timezone
    tz_name = get_timezone_name(lat, lon)
    if tz_name:
        print(f"Detected timezone: {tz_name}")
    else:
        print("⚠️ Could not detect timezone automatically.")
        tz_name = input("Enter timezone name (e.g., Asia/Kolkata) or UTC offset hours (e.g., +5.5): ").strip()

    # 4) get local time with robust validation
    while True:
        time_input = input("Enter local clock time (HH:MM) [default 12:00]: ").strip() or "12:00"
        try:
            if ":" in time_input:
                hour_part, min_part = map(int, time_input.split(":"))
                if not (0 <= hour_part <= 23 and 0 <= min_part <= 59):
                    raise ValueError("Hour must be 0-23 and minute 0-59")
                local_clock_hours = hour_part + min_part / 60.0
            else:
                local_clock_hours = float(time_input)
                if not (0 <= local_clock_hours < 24):
                    raise ValueError("Decimal hours must be between 0 and 24")
            break
        except ValueError as e:
            print(f"⚠️ Invalid time: {e}. Please enter again in HH:MM or decimal hours format.")


    # 5) compute UTC offset
    offset_hours = None
    if tz_name.startswith(("+", "-")):
        try:
            offset_hours = float(tz_name)
        except:
            offset_hours = None

    if offset_hours is None:
        while True:
            try:
                tz = pytz.timezone(tz_name)
                if ":" in time_input:
                    hour_part, min_part = map(int, time_input.split(":"))
                else:
                    hour_part = int(float(time_input))
                    min_part = int((float(time_input) - hour_part) * 60)
                naive_dt = datetime.strptime(f"{date_str} {hour_part:02d}:{min_part:02d}", "%Y-%m-%d %H:%M")
                local_dt = tz.localize(naive_dt, is_dst=None)
                offset_seconds = local_dt.utcoffset().total_seconds()
                offset_hours = offset_seconds / 3600.0
                break
            except Exception as e:
                print(f"⚠️ Could not determine timezone automatically: {e}")
                while True:
                    try:
                        offset_hours = float(input("Enter UTC offset in hours (e.g., 5.5 for IST): "))
                        break
                    except ValueError:
                        print("⚠️ Invalid number. Enter numeric UTC offset like 5.5 or -4.0")
                break

    print(f"UTC offset (hours): {offset_hours}")

    # 6) compute Equation of Time and LSTM & Time Correction
    decl = solar_declination(day)
    eot_min = equation_of_time(day)
    LSTM = 15 * offset_hours
    TC_min = 4 * (lon - LSTM) + eot_min
    LST_hours = local_clock_hours + TC_min / 60.0

    print(f"Day: {day}, Declination: {round(decl,2)}°")
    print(f"Equation of Time: {round(eot_min,2)} min")
    print(f"LSTM (deg): {round(LSTM,3)}, Time Correction: {round(TC_min,2)} min")
    print(f"Local clock time: {time_input} -> Local Solar Time: {LST_hours:.4f} hours")

    t_solar = LST_hours

    # --- Sunrise and Sunset Calculation ---
    phi = deg2rad(lat)
    delta = deg2rad(decl)
    try:
        H0_rad = math.acos(-math.tan(phi) * math.tan(delta))
        H0_deg = rad2deg(H0_rad)
        sunrise_LST = 12 - H0_deg / 15
        sunset_LST = 12 + H0_deg / 15
        sunrise_local = sunrise_LST - TC_min/60
        sunset_local = sunset_LST - TC_min/60
        def hours_to_hm(hours):
            h = int(hours)
            m = int((hours - h) * 60)
            return f"{h:02d}:{m:02d}"
        print(f"Sunrise (local): {hours_to_hm(sunrise_local)}")
        print(f"Sunset  (local): {hours_to_hm(sunset_local)}")
    except ValueError:
        print("⚠️ Sun does not rise/set on this date at this latitude (polar day/night).")

    # 7) compute yantras
    results = compute_all_yantras(lat, decl, t_solar)
    print(json.dumps(results, indent=4))
