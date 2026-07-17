import os
import urllib.request
import json
from datetime import datetime, timedelta

def main():
    # We want to log the previous day (or current day if triggered manually)
    # Let's get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    year = yesterday.strftime("%Y")
    date_str = yesterday.strftime("%d-%m") # DD-MM format
    
    # URL of yesterday's historical log in Firebase
    firebase_url = f"https://purulia-weather-station-default-rtdb.asia-southeast1.firebasedatabase.app/history/{year}/{date_str}.json"
    
    try:
        req = urllib.request.Request(firebase_url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        if not data:
            print(f"No log data found for date: {date_str} in year {year}")
            return
            
        # Parse records
        records = []
        for time_key, val in data.items():
            try:
                temp = float(val.get("temp", 0))
                humi = float(val.get("humi", 0))
                pres = float(val.get("pres", 0))
                records.append({
                    "time": time_key.replace("-", ":"),
                    "temp": temp,
                    "humi": humi,
                    "pres": pres
                })
            except Exception as e:
                continue
                
        if not records:
            print("No valid records found in dataset.")
            return
            
        # Sort chronologically by time
        records.sort(key=lambda x: x["time"])
        
        # Find min/max values
        min_temp = min(r["temp"] for r in records)
        max_temp = max(r["temp"] for r in records)
        min_humi = min(r["humi"] for r in records)
        max_humi = max(r["humi"] for r in records)
        
        # Format strings for log output
        log_lines = []
        for r in records:
            highlights = []
            if r["temp"] == min_temp:
                highlights.append("LOW TEMP ❄️")
            if r["temp"] == max_temp:
                highlights.append("HIGH TEMP 🔥")
            if r["humi"] == min_humi:
                highlights.append("LOW HUMIDITY 🏜️")
            if r["humi"] == max_humi:
                highlights.append("HIGH HUMIDITY 💧")
                
            highlight_str = f" [{', '.join(highlights)}]" if highlights else ""
            line = f"[{r['time']}] Temp: {r['temp']:.1f}°C, Humidity: {r['humi']:.1f}%, Pressure: {r['pres']:.0f} hPa{highlight_str}"
            log_lines.append(line)
            
        # Write to local file
        folder_path = os.path.join("Data", year, date_str)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, "notepad.txt")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines) + "\n")
            
        print(f"Successfully generated log file: {file_path}")
        
    except Exception as e:
        print(f"Error fetching logs from Firebase: {e}")

if __name__ == "__main__":
    main()
