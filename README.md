# Vehicle Tracking & Counting System

A computer vision-based vehicle tracking and counting application built using **Python, YOLO11, OpenCV, FastAPI, PostgreSQL, and Streamlit**.

The system processes traffic videos, detects and tracks vehicles, counts line crossings by direction, stores results in a PostgreSQL database, and displays analytics through a web dashboard.

## Features

- **Vehicle Detection:** Detect vehicles such as cars, trucks, and buses using YOLO11.
- **Object Tracking:** Track detected vehicles across video frames.
- **Directional Counting:** Count vehicles crossing configured red and blue lines in the UP and DOWN directions.
- **Video Processing:** Generate processed videos with vehicle bounding boxes, track IDs, and count overlays.
- **REST API:** Upload videos and retrieve video records and vehicle counts using FastAPI.
- **PostgreSQL Integration:** Persist video metadata and vehicle counts.
- **Live Processing Preview:** Retrieve the latest processed frame and current counts through live API endpoints.
- **Interactive Dashboard:** Display vehicle statistics, direction-wise counts, charts, processed video previews, and video history using Streamlit.

## Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Object Detection | YOLO11 |
| Computer Vision | OpenCV |
| Backend API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Dashboard | Streamlit |
| Data Analysis | Pandas, NumPy |
| Visualization | Plotly |

## Project Structure

```text
vehicle-tracking-counting/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   ├── init_db.py
│   │   │   └── models.py
│   │   ├── services/
│   │   │   └── video_service.py
│   │   ├── live_state.py
│   │   └── main.py
│   ├── test_db.py
│   ├── test_video_integration.py
│   └── test_video_service.py
├── computer_vision/
│   ├── models/
│   ├── counter.py
│   ├── detector.py
│   ├── tracker.py
│   ├── video_processor.py
│   └── run_processor.py
├── dashboard/
│   └── app.py
├── test_videos/
├── output/
├── uploads/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

*The structure above describes the main project components; local test files and generated assets may vary.*

## Prerequisites

Install the following before running the project:

- Python 3.11
- PostgreSQL
- Git
- YOLO11 model weights

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/vehicle-tracking-counting.git
cd vehicle-tracking-counting
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, you can run the environment's Python directly using `.\.venv\Scripts\python.exe`.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named `vehicle_tracking`.

Create a local `.env` file in the project root using the following template:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vehicle_tracking
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
```

Replace the example credentials with your local PostgreSQL credentials.

**Security:** Never commit `.env` or publish database passwords.

Initialize the database using the project's database initialization code, if required by the current implementation.

### 5. Download YOLO11 weights

The model weights are excluded from Git because they are large binary files.

Create or use the `computer_vision/models/` directory and place the required weights there:

- `yolo11s.pt`
- `yolo11n.pt` (if needed by your selected scripts)

The tracker currently expects `computer_vision/models/yolo11s.pt` by default. Ensure the required weights exist before processing videos.

## Running the Application

Open two PowerShell terminals from the project root.

### Terminal 1: Start FastAPI

```powershell
python -m uvicorn backend.app.main:app --reload
```

API base URL:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### Terminal 2: Start Streamlit Dashboard

```powershell
python -m streamlit run dashboard/app.py
```

Dashboard URL:

`http://localhost:8501`

Keep FastAPI running while using the dashboard.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API root |
| GET | `/health` | Health check |
| GET | `/videos` | Retrieve video records |
| GET | `/videos/{video_id}/counts` | Retrieve counts for a video |
| POST | `/videos/upload` | Upload and start processing a video |
| GET | `/live/status` | Retrieve current processing status and counts |
| GET | `/live/frame` | Retrieve the latest processed frame |

See the FastAPI Swagger documentation for request and response details.

## How It Works

1. Upload a traffic video through the dashboard or API.
2. The backend validates and stores the uploaded file.
3. YOLO11 detects vehicles in video frames.
4. The tracking component associates detected vehicles across frames.
5. The counting component records crossings of the configured lines.
6. The processed video is written to the output directory.
7. Video metadata and vehicle counts are saved to PostgreSQL after successful processing.
8. The dashboard displays live processing information, saved counts, charts, and video history.

## Notes

- Live preview currently retrieves the latest available processed frame; it is not a full WebSocket or continuous video stream.
- Vehicle counts depend on video quality, camera angle, detection performance, and counting-line placement.
- Uploaded videos, generated output files, model weights, and local environment files are intentionally excluded from Git.
- The live processing state is held in application memory, while completed video results are stored in PostgreSQL.

## Future Improvements

- Real-time video streaming
- Processing progress percentage
- Improved tracking and duplicate-count prevention
- Background job queue and processing history
- Dashboard filters and date-wise analytics
- Automated tests and deployment configuration

## Author

**Shoeb Raza**

GitHub: https://github.com/razashoeb07

LinkedIn: https://www.linkedin.com/in/shoebraza02/

Portfolio: https://shoebraza-portfolio.vercel.app/
