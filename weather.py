#!/usr/bin/python3
import requests
import os
from google.cloud import texttospeech
from datetime import datetime, timedelta
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1

#Change Me
ouput_file="/path/to/output/weather_update.mp3"
radio_station="Radio Station Name"
weather_report_name="Weather Update"
WEATHER_API_KEY = 'your_weather_apiKey'

local_time = datetime.now()
print("Local time:", local_time)

# Set the path to your Google service account JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/radio_weather_report/service_account_key.json"

# Set your Weather.com API key and location details
LATITUDE = '41.0360'  # Latitude for Morgan, Utah
LONGITUDE = '-111.6888'  # Longitude for Morgan, Utah
LANGUAGE = 'en-US'
UNIT_SYSTEM = 'e'  # Use 'e' for imperial, 'm' for metric

# Define the exact URLs from the code snippet
CURRENT_URL = ('https://api.weather.com/v3/wx/observations/current'
               '?geocode={latitude},{longitude}&language={language}&format=json&apiKey={api_key}&units={units}')
DAILY_URL = ('https://api.weather.com/v3/wx/forecast/daily/15day'
             '?geocode={latitude},{longitude}&language={language}&format=json&apiKey={api_key}&units={units}')
HOURLY_URL = ('https://api.weather.com/v3/wx/forecast/hourly/15day'
              '?geocode={latitude},{longitude}&language={language}&format=json&apiKey={api_key}&units={units}')

def build_url(base_url):
    """Build the URL with parameters."""
    return base_url.format(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        language=LANGUAGE,
        api_key=WEATHER_API_KEY,
        units=UNIT_SYSTEM
    )

def fetch_weather_data():
    """Fetch current, daily, and hourly weather data."""
    try:
        current_url = build_url(CURRENT_URL)
        daily_url = build_url(DAILY_URL)
        hourly_url = build_url(HOURLY_URL)

        # Request data from each URL
        current_response = requests.get(current_url)
        daily_response = requests.get(daily_url)
        hourly_response = requests.get(hourly_url)

        # Parse JSON responses if they are successful
        current_data = current_response.json() if current_response.status_code == 200 else None
        daily_data = daily_response.json() if daily_response.status_code == 200 else None
        hourly_data = hourly_response.json() if hourly_response.status_code == 200 else None

        # Ensure all data is retrieved
        if not current_data or not daily_data or not hourly_data:
            raise ValueError("Incomplete data received from Weather.com")

        return {
            "current": current_data,
            "daily": daily_data,
            "hourly": hourly_data
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def generate_weather_report(weather_data):
    """Generate a detailed weather report."""
    # Current weather
    current_temp = weather_data["current"].get('temperature')
    current_conditions = weather_data["current"].get('wxPhraseLong')

    report = (f"Hi there! Here's your hourly forecast from Morgan Valley Radio! Currently, in Morgan Utah, the temperature is {current_temp} degrees. "
              f"The weather is {current_conditions}. ")

    # 8-hour forecast in 2-hour increments
    report += "As for the next 6 hours, "
    for i in range(0, 6, 2):  # 2-hour increments
        temp = weather_data["hourly"].get("temperature", [None])[i]
        conditions = weather_data["hourly"].get("wxPhraseLong", ["Conditions unavailable"])[i]
        time = datetime.now() + timedelta(hours=i)
        report += f"At {time.strftime('%I %p')}, {temp} degrees and {conditions}. "

    # 3-day forecast
    report += "And looking at the next 3 days: "
    for day in range(3):
        narrative = weather_data["daily"].get("narrative", ["Forecast unavailable"])[day]
    
        # Get the day name: "Today" for the current day, then weekday names
        if day == 0:
            day_name = "Today"
        else:
            day_name = weather_data["daily"].get("dayOfWeek", ["Today", "Tomorrow", "Next Day"])[day]
        report += f"{day_name}, {narrative}. "

    report += "Thanks for tuning in to MVRC, Morgan Valley Radio, and we hope you have a great rest of your day!"
    
    return report

def text_to_speech(report):
    """Convert the weather report to realistic speech and save as MP3."""
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=report)
    voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-I",
    ssml_gender=texttospeech.SsmlVoiceGender.MALE
)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Generate the speech
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Save the audio as an MP3 file
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"weather_report.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f"Weather report saved as {filename}")
    return filename

def add_background_music_with_fade(voice_file, music_file, output_file, 
                                   music_volume=-8, fade_in_duration=1000, fade_out_duration=1500):
    """
    Adds background music to a voice audio file with fade-in and fade-out effects.

    Parameters:
    - voice_file: str - Path to the synthesized voice audio file.
    - music_file: str - Path to the background music audio file.
    - output_file: str - Path to the output file.
    - music_volume: int - Volume adjustment for the music in dB.
    - fade_in_duration: int - Duration of the fade-in effect in milliseconds.
    - fade_out_duration: int - Duration of the fade-out effect in milliseconds.
    """
    # Load the voice audio and background music
    voice = AudioSegment.from_file(voice_file)
    music = AudioSegment.from_file(music_file)

    # Adjust music volume
    music = music - abs(music_volume) 

    # Loop or trim the background music to match the length of the voice
    if len(music) < len(voice):
        music = music * (len(voice) // len(music) + 1)
    music = music[:len(voice)]

    # Apply fade-in and fade-out effects to the music
    music = music.fade_in(fade_in_duration).fade_out(fade_out_duration)

    # Overlay voice onto music
    combined = music.overlay(voice)

    # Export the combined audio
    combined.export(output_file, format="mp3")
    audio_file = MP3(output_file, ID3=ID3)
    
    # Add metadata tags
    audio_file["TPE1"] = TPE1(encoding=3, text=radio_station)  # Artist tag
    audio_file["TIT2"] = TIT2(encoding=3, text=weather_report_name)   # Title tag
    
    # Save the metadata changes
    audio_file.save()
    print(f"Saved report with background music and fades as '{output_file}'.")

def main():
    weather_data = fetch_weather_data()
    if weather_data:
        report = generate_weather_report(weather_data)
        #print("Generated Report:", report)
        add_background_music_with_fade(text_to_speech(report), "/etc/radio_weather_report/music.mp3")

if __name__ == "__main__":
    main()
