
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "output"
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Live Traffic Monitor",
    page_icon="🚦",
    layout="wide",
)

st.title("🚦 Live Traffic Monitor")
st.caption("Vehicle Tracking & Counting System")
st.divider()


# --------------------------------------------------
# API Helpers
# --------------------------------------------------

@st.cache_data(ttl=5)
def fetch_videos():
    response = requests.get(f"{API_URL}/videos", timeout=10)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=5)
def fetch_counts(video_id):
    response = requests.get(
        f"{API_URL}/videos/{video_id}/counts",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_live_status():
    response = requests.get(
        f"{API_URL}/live/status",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def upload_video(file):
    return requests.post(
        f"{API_URL}/videos/upload",
        files={
            "file": (
                file.name,
                file.getvalue(),
                file.type or "video/mp4",
            )
        },
        timeout=(10, 120),
    )


# --------------------------------------------------
# Sidebar: Upload and Controls
# --------------------------------------------------

st.sidebar.header("Dashboard Controls")
st.sidebar.subheader("Upload Traffic Video")

uploaded_file = st.sidebar.file_uploader(
    "Choose a traffic video",
    type=["mp4", "avi", "mov", "mkv"],
    help="Upload a video to detect and count vehicles.",
)

if st.sidebar.button(
    "Upload & Process Video",
    use_container_width=True,
    disabled=uploaded_file is None,
):
    try:
        with st.spinner("Uploading video..."):
            response = upload_video(uploaded_file)

        if response.ok:
            result = response.json()
            st.session_state["live_monitoring"] = True
            st.session_state["uploaded_filename"] = result.get(
                "filename", uploaded_file.name
            )
            st.session_state["upload_message"] = result.get(
                "message", "Video uploaded successfully."
            )
            st.cache_data.clear()
            st.rerun()
        else:
            st.sidebar.error(
                f"Upload failed ({response.status_code}): "
                f"{response.text}"
            )

    except requests.exceptions.RequestException as error:
        st.sidebar.error(f"API connection error: {error}")


if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# --------------------------------------------------
# Live Processing Panel
# --------------------------------------------------

if st.session_state.get("live_monitoring", False):
    st.subheader("🎥 Live Video Processing")

    st.write(
        "Uploaded video:",
        st.session_state.get("uploaded_filename", "Unknown"),
    )

    status_placeholder = st.empty()
    frame_placeholder = st.empty()
    live_metrics_placeholder = st.empty()
    live_error_placeholder = st.empty()

    try:
        while st.session_state.get("live_monitoring", False):
            live = get_live_status()
            status = live.get("status", "unknown")
            counts = live.get("counts") or {}

            down = counts.get("down") or {}
            up = counts.get("up") or {}

            # Combine UP and DOWN counts by vehicle type
            vehicle_types = set(down) | set(up)

            totals = {
                vehicle_type: (
                    int(down.get(vehicle_type, 0))
                    + int(up.get(vehicle_type, 0))
                )
                for vehicle_type in vehicle_types
            }

            total_vehicles = sum(totals.values())
            cars = totals.get("car", 0)
            trucks = totals.get("truck", 0)
            buses = totals.get("bus", 0)

            status_placeholder.info(
                f"Processing status: {status.upper()}"
            )

            with live_metrics_placeholder.container():
                metric1, metric2, metric3, metric4 = st.columns(4)
                metric1.metric("Total Vehicles", total_vehicles)
                metric2.metric("Cars", cars)
                metric3.metric("Trucks", trucks)
                metric4.metric("Buses", buses)

                direction1, direction2 = st.columns(2)
                direction1.metric(
                    "🔴 DOWN Traffic",
                    sum(int(value) for value in down.values()),
                )
                direction2.metric(
                    "🔵 UP Traffic",
                    sum(int(value) for value in up.values()),
                )

            # Fetch the latest available frame
            frame_response = requests.get(
                f"{API_URL}/live/frame",
                timeout=10,
            )

            if frame_response.status_code == 200:
                frame_placeholder.image(
                    frame_response.content,
                    caption="Latest processed frame",
                    use_container_width=True,
                )
            elif frame_response.status_code != 204:
                live_error_placeholder.warning(
                    "Could not retrieve the latest video frame."
                )

            if status == "completed":
                status_placeholder.success(
                    "✅ Video processing completed successfully."
                )
                st.session_state["live_monitoring"] = False
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()

            elif status == "failed":
                live_error_placeholder.error(
                    f"Video processing failed: "
                    f"{live.get('error') or 'Unknown error'}"
                )
                st.session_state["live_monitoring"] = False
                break

            elif status == "idle":
                status_placeholder.warning(
                    "Waiting for video processing to start..."
                )

            time.sleep(0.3)

    except requests.exceptions.RequestException as error:
        live_error_placeholder.error(
            f"Could not connect to the live API: {error}"
        )

    st.divider()


# --------------------------------------------------
# Main Dashboard: Database Records
# --------------------------------------------------

try:
    videos = fetch_videos()

    if not videos:
        st.info(
            "No video records are available in the database yet. "
            "Upload a video from the sidebar to get started."
        )
        st.stop()

    # API returns the video list; select the latest record.
    latest_video = videos[0]
    video_id = latest_video["id"]

    result = fetch_counts(video_id)
    counts = result.get("counts", [])

    df = pd.DataFrame(counts)

    if df.empty:
        df = pd.DataFrame(
            columns=["vehicle_type", "direction", "count"]
        )

    # Ensure count data is numeric.
    if not df.empty:
        df["count"] = pd.to_numeric(
            df["count"], errors="coerce"
        ).fillna(0)

    # Direction totals.
    down_total = int(
        df.loc[df["direction"] == "down", "count"].sum()
    )
    up_total = int(
        df.loc[df["direction"] == "up", "count"].sum()
    )

    # Vehicle type totals.
    vehicle_totals = (
        df.groupby("vehicle_type")["count"].sum().to_dict()
        if not df.empty
        else {}
    )

    cars = int(vehicle_totals.get("car", 0))
    trucks = int(vehicle_totals.get("truck", 0))
    buses = int(vehicle_totals.get("bus", 0))
    total_vehicles = int(df["count"].sum()) if not df.empty else 0

    # --------------------------------------------------
    # Traffic Overview
    # --------------------------------------------------

    st.subheader("📊 Traffic Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Vehicles", total_vehicles)
    col2.metric("Cars", cars)
    col3.metric("Trucks", trucks)
    col4.metric("Buses", buses)

    col1, col2 = st.columns(2)
    col1.metric("🔴 DOWN Traffic", down_total)
    col2.metric("🔵 UP Traffic", up_total)

    st.divider()

    # --------------------------------------------------
    # Latest Video Information
    # --------------------------------------------------

    st.subheader("📹 Latest Processed Video")

    info1, info2, info3, info4 = st.columns(4)

    info1.metric("Video ID", latest_video["id"])

    duration = latest_video.get("duration")
    fps = latest_video.get("fps")

    info2.metric(
        "Duration",
        f"{duration:.2f} sec" if duration is not None else "N/A",
    )
    info3.metric(
        "FPS",
        f"{fps:.2f}" if fps is not None else "N/A",
    )
    info4.metric(
        "Resolution",
        latest_video.get("resolution") or "N/A",
    )

    st.write("**Filename:**", latest_video.get("filename", "N/A"))
    st.write("**Status:**", latest_video.get("status", "N/A"))

    # --------------------------------------------------
    # Processed Video Preview
    # --------------------------------------------------

    st.subheader("🎬 Processed Video Preview")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    processed_files = list(
        OUTPUT_DIR.glob("processed_*.mp4")
    )

    processed_files.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if processed_files:
        selected_video = st.selectbox(
            "Select a processed video",
            processed_files,
            format_func=lambda path: path.name,
        )

        st.video(str(selected_video))
    else:
        st.warning(
            "No processed video found. Upload and process a video first."
        )

    st.divider()

    # --------------------------------------------------
    # Vehicle Count Charts
    # --------------------------------------------------

    st.subheader("📈 Vehicle Count Analysis")

    if not df.empty:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            type_df = (
                df.groupby("vehicle_type", as_index=False)["count"]
                .sum()
            )

            fig = px.bar(
                type_df,
                x="vehicle_type",
                y="count",
                title="Vehicles by Type",
                labels={
                    "vehicle_type": "Vehicle Type",
                    "count": "Count",
                },
                text="count",
            )

            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            direction_df = (
                df.groupby("direction", as_index=False)["count"]
                .sum()
            )

            fig = px.bar(
                direction_df,
                x="direction",
                y="count",
                title="Traffic by Direction",
                labels={
                    "direction": "Direction",
                    "count": "Count",
                },
                text="count",
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detailed Vehicle Counts")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No vehicle counts are available for this video yet.")

    # --------------------------------------------------
    # Video History
    # --------------------------------------------------

    st.divider()
    st.subheader("🗂️ Video History")

    history_df = pd.DataFrame(videos)

    display_columns = [
        "id",
        "filename",
        "status",
        "duration",
        "fps",
        "resolution",
        "uploaded_at",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in history_df.columns
    ]

    st.dataframe(
        history_df[available_columns],
        use_container_width=True,
        hide_index=True,
    )

except requests.exceptions.ConnectionError:
    st.error(
        "FastAPI is not connecting. Start the Uvicorn server first."
    )

except requests.exceptions.RequestException as error:
    st.error(f"API request failed: {error}")

except Exception as error:
    st.error(f"Dashboard error: {error}")
