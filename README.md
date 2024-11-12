# Weather Report Generator for Radio Station

This Python program fetches weather data from Weather.com, generates a speech-based weather report, and outputs it as an MP3 file with background music for radio stations. The report includes current weather, an 8-hour forecast in 2-hour increments, and a 3-day forecast.
## Sample

https://github.com/user-attachments/assets/7dbacf08-3526-40a5-9f00-4a80970c169f

## Features

- Fetches current, hourly, and daily weather data from Weather.com API.
- Generates a detailed weather report with temperature, conditions, and forecasts.
- Converts the weather report text into speech using Google Cloud Text-to-Speech API.
- Adds background music with fade-in and fade-out effects to the speech audio.
- Outputs the final weather report as an MP3 file with metadata tags.

## Requirements
- Python 3.7 or higher
- `requests` library
- `google-cloud-texttospeech` library
- `pydub` library
- `mutagen` library

## Setup

### Step 1: Google Cloud Service Account Key
To use the Google Cloud Text-to-Speech API, you need to create a Google Cloud service account and download a JSON key.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **IAM & Admin** > **Service Accounts**.
4. Click **Create Service Account**.
5. Enter a name for the service account and click **Create**.
6. Grant the service account **Editor** permissions.
7. Under **Keys**, click **Add Key** > **Create new key** and select **JSON**.
8. Download the JSON key file.
9. Save the file to a folder called /etc/radio_weather_report/

Place this file in a secure location, and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of this file in your system.

### Step 2: Weather.com API Key
To fetch weather data, you need to obtain a Weather.com API key.

1. Open [wunderground.com](https://www.wunderground.com) (Wunderground is owned by Weather.com).
2. Right-click on the page and select **View Page Source**.
3. Search for `"apiKey"` in the source code.
4. Copy the value of the API key.

### Step 3: Install Dependencies
Install the required Python libraries:

- `requests`
- `google-cloud-texttospeech`
- `pydub`
- `mutagen`

### Step 4: Setup Your Cron Job
To run the weather report generation script automatically, you can create a cron job.

1. Open your crontab file by running:

   `crontab -e`

2. Add the following line to run the script every hour on the half hour:

   `5 * * * * /usr/bin/python3 /path/to/weather.py >> /path/for/log/weather.log 2>&1`

This cron job will execute the script every hour at minute 5, logging output to `/path/for/log/weather.log`.

### Step 5: Customize Script Variables
In the script, make sure to customize the following variables:
- `output_file`: The path where the weather report MP3 file will be saved.
- `radio_station`: The name of your radio station.
- `weather_report_name`: The name you want for the weather report.
- `WEATHER_API_KEY`: The key you retrieved from wunderground.com
- `LATITUDE` = Latitude for Radio Station
- `LONGITUDE` = Longitude for Radio Station

### Step 6: Add music
1. Pick a royalty-free background music track. You can find suitable music on sites like YouTube Audio Library, Free Music Archive, or Incompetech.
2. Download file to /etc/radio_weather_report as music.mp3
### Step 7: Run the Script
Run the script manually to generate a weather report.

The script will fetch weather data, generate the weather report, convert it to speech, and output the report as an MP3 file with background music.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- The Google Cloud Text-to-Speech API provides high-quality voice synthesis.
- The Weather.com API provides accurate weather data.
