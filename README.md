# Geospatial Sales Insights Map

This is a dynamic and interactive web application built with Python Flask, Pandas, and Folium. It allows users to upload a CSV or Excel file containing customer data, calculates the average sales, and generates an interactive map plotting customer locations with dynamic color coding.

## Project Structure
- `app.py`: The Flask backend server that handles file validation, data processing with Pandas, and map generation with Folium.
- `templates/index.html`: The frontend user interface for uploading files and displaying the generated map.
- `static/style.css`: Modern styling with a premium dark theme, animations, and responsive layout.
- `static/script.js`: Client-side logic for handling asynchronous form submission, dynamic UI updates, and iframe reloading.
- `requirements.txt`: Python package dependencies for the project.
- `sample_data.csv`: A sample dataset to test the application.

## Prerequisites
- Python 3.8+ installed on your system.

## Setup Instructions

### 1. Open Terminal/Command Prompt
Navigate to the root directory where you extracted the project.
```bash
cd c:/Users/RajeevK/Desktop/Product/flask_sales_map
```

### 2. Create a Virtual Environment
It is recommended to run Python projects within an isolated virtual environment to avoid dependency conflicts.
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
**On Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```
*(If you are using regular Command Prompt, run: `.\venv\Scripts\activate.bat`)*

### 4. Install Dependencies
Run the following command to install the required libraries (Flask, pandas, folium, openpyxl, etc.):
```bash
pip install -r requirements.txt
```

### 5. Run the Application
Start the Flask development server:
```bash
python app.py
```

### 6. View in Browser
Open your preferred web browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

## How to use the App
1. On the web page, click **"Choose CSV/Excel File"**.
2. Select the provided `sample_data.csv` (or any file matching the required schema).
3. Click **"Generate Map"**.
4. The application will asynchronously process your data and smoothly scroll down to present an interactive map.
5. In the map, green markers represent customers with sales >= the global average, while red markers represent sales < average. 
6. Click or hover on the markers to view detailed customer information.
