# TCX → CSV Converter

A simple Streamlit app that converts Garmin TCX workout files into three CSVs:  
- `activities.csv`  
- `laps.csv`  
- `tracks.csv`

## Features

- Upload a `.tcx` file in your browser  
- In-memory parsing—no need for local file dialogs  
- Download each CSV with one click  
- Pure Python, zero-JS!

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
