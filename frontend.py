"""
Streamlit Frontend for Smart Agriculture Platform
Interactive dashboard for monitoring and control
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# Backend API configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Smart Agriculture Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-critical {
        background-color: #ffebee;
        padding: 1rem;
        border-left: 4px solid #c62828;
        border-radius: 0.25rem;
    }
    .alert-warning {
        background-color: #fff8e1;
        padding: 1rem;
        border-left: 4px solid #f57f17;
        border-radius: 0.25rem;
    }
    .alert-success {
        background-color: #e8f5e9;
        padding: 1rem;
        border-left: 4px solid #2e7d32;
        border-radius: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def make_api_request(endpoint, method="GET", data=None):
    """Helper function for API requests with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ Cannot connect to backend API. Please ensure the backend server is running."
        )
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ API Error: {e}")
        return None
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")
        return None


def display_sensor_metrics(sensor_data):
    """Display current sensor readings as metrics"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💧 Soil Moisture",
            value=f"{sensor_data['soil_moisture']:.1f}%",
            delta=None,
        )

    with col2:
        st.metric(
            label="🌡️ Temperature",
            value=f"{sensor_data['temperature']:.1f}°C",
            delta=None,
        )

    with col3:
        st.metric(
            label="💨 Humidity", value=f"{sensor_data['humidity']:.1f}%", delta=None
        )


def display_recommendations(recommendations):
    """Display irrigation and fertilizer recommendations"""
    st.subheader("💡 Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💧 Irrigation")
        action = recommendations["irrigation_action"]

        if action == "water":
            st.success(f"**Action:** Water the crops")
            st.info(f"**Amount:** {recommendations['irrigation_amount']:.2f} liters/m²")
        elif action == "reduce":
            st.warning(f"**Action:** Reduce or stop irrigation")
        else:
            st.success(f"**Action:** No irrigation needed")

        with st.expander("📋 View Reasoning"):
            st.write(recommendations["irrigation_reasoning"])

    with col2:
        st.markdown("#### 🌾 Fertilizer")
        action = recommendations["fertilizer_action"]

        if action == "apply":
            st.success(f"**Action:** Apply fertilizer")
            st.info(f"**Type:** {recommendations['fertilizer_type']}")
        else:
            st.info(f"**Action:** No fertilizer needed")

        with st.expander("📋 View Reasoning"):
            st.write(recommendations["fertilizer_reasoning"])


def display_alerts(recommendations):
    """Display alert notifications"""
    alert_level = recommendations["alert_level"]
    alert_message = recommendations["alert_message"]

    if alert_level == "critical":
        st.markdown(
            f"""
            <div class="alert-critical">
                <h3>🚨 Critical Alert</h3>
                <p>{alert_message}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    elif alert_level == "warning":
        st.markdown(
            f"""
            <div class="alert-warning">
                <h3>⚠️ Warning</h3>
                <p>{alert_message}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="alert-success">
                <h3>✅ All Systems Normal</h3>
                <p>No alerts at this time. Conditions are within acceptable range.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )


def plot_sensor_history(sensor_data_list):
    """Create interactive plots for sensor history"""
    if not sensor_data_list:
        st.info("No historical data available yet.")
        return

    df = pd.DataFrame(sensor_data_list)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Create subplots
    col1, col2, col3 = st.columns(3)

    with col1:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["soil_moisture"],
                mode="lines+markers",
                name="Soil Moisture",
                line=dict(color="#1976D2", width=2),
            )
        )
        fig.update_layout(
            title="Soil Moisture Over Time",
            xaxis_title="Time",
            yaxis_title="Moisture (%)",
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["temperature"],
                mode="lines+markers",
                name="Temperature",
                line=dict(color="#D32F2F", width=2),
            )
        )
        fig.update_layout(
            title="Temperature Over Time",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["humidity"],
                mode="lines+markers",
                name="Humidity",
                line=dict(color="#388E3C", width=2),
            )
        )
        fig.update_layout(
            title="Humidity Over Time",
            xaxis_title="Time",
            yaxis_title="Humidity (%)",
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application"""

    # Header
    st.markdown(
        '<div class="main-header">🌱 Smart Agriculture Platform</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Get available crops
        crops_response = make_api_request("/api/crops")
        if crops_response:
            crop_options = list(crops_response["crops"].keys())
            selected_crop = st.selectbox("Select Crop Type", crop_options, index=0)
        else:
            selected_crop = "default"

        st.markdown("---")

        st.header("📊 System Statistics")
        stats_response = make_api_request("/api/stats")
        if stats_response and stats_response.get("success"):
            stats = stats_response
            st.metric("Total Readings", stats["total_readings"])
            st.metric("Total Recommendations", stats["total_recommendations"])

            st.markdown("**Average Values:**")
            st.write(f"Moisture: {stats['averages']['soil_moisture']:.1f}%")
            st.write(f"Temperature: {stats['averages']['temperature']:.1f}°C")
            st.write(f"Humidity: {stats['averages']['humidity']:.1f}%")

            st.markdown("**Alert Summary:**")
            st.write(f"🚨 Critical: {stats['alert_counts']['critical']}")
            st.write(f"⚠️ Warning: {stats['alert_counts']['warning']}")
            st.write(f"✅ Normal: {stats['alert_counts']['none']}")

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔬 Sensor Input", "📜 History"])

    with tab1:
        st.header("Current Status")

        # Get latest data
        sensor_response = make_api_request("/api/sensor-data/latest?limit=1")
        rec_response = make_api_request("/api/recommendations/latest?limit=1")

        if sensor_response and rec_response:
            if sensor_response and rec_response:
                latest_sensor = sensor_response[0]
                latest_rec = rec_response[0]

                # Display alerts first (most important)
                display_alerts(latest_rec)

                st.markdown("---")

                # Current sensor readings
                st.subheader("📈 Current Readings")
                display_sensor_metrics(latest_sensor)

                st.markdown("---")

                # Recommendations
                display_recommendations(latest_rec)
            else:
                st.info("No data available. Please submit sensor data first.")

        # Historical charts
        st.markdown("---")
        st.subheader("📊 Historical Trends")
        history_response = make_api_request("/api/sensor-data/latest?limit=20")
        if history_response:
            plot_sensor_history(history_response)

    with tab2:
        st.header("🔬 Submit Sensor Data")

        col1, col2 = st.columns(2)

        with col1:
            soil_moisture = st.slider("Soil Moisture (%)", 0.0, 100.0, 50.0, 0.1)
            temperature = st.slider("Temperature (°C)", -10.0, 50.0, 25.0, 0.1)
            humidity = st.slider("Humidity (%)", 0.0, 100.0, 60.0, 0.1)

        with col2:
            location = st.text_input("Location", "Field-1")

            st.markdown("**Quick Presets:**")
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("☀️ Hot & Dry"):
                    soil_moisture = 35.0
                    temperature = 35.0
                    humidity = 30.0

            with col_b:
                if st.button("🌧️ Rainy"):
                    soil_moisture = 85.0
                    temperature = 20.0
                    humidity = 90.0

            with col_c:
                if st.button("✅ Optimal"):
                    soil_moisture = 65.0
                    temperature = 24.0
                    humidity = 70.0

        st.markdown("---")

        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("📤 Submit Data", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    data = {
                        "soil_moisture": soil_moisture,
                        "temperature": temperature,
                        "humidity": humidity,
                        "location": location,
                        "crop_type": selected_crop,
                    }

                    response = make_api_request(
                        "/api/sensor-data", method="POST", data=data
                    )

                    if response and response.get("success"):
                        st.success("✅ Data submitted successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit data")

        with col2:
            if st.button("🔍 Analyze Without Saving", use_container_width=True):
                with st.spinner("Analyzing..."):
                    data = {
                        "soil_moisture": soil_moisture,
                        "temperature": temperature,
                        "humidity": humidity,
                        "location": location,
                        "crop_type": selected_crop,
                    }

                    response = make_api_request(
                        "/api/analyze", method="POST", data=data
                    )

                    if response and response.get("success"):
                        analysis = response["analysis"]

                        st.markdown("### Analysis Results")
                        display_alerts(
                            {
                                "alert_level": analysis["alerts"]["level"],
                                "alert_message": " | ".join(
                                    analysis["alerts"]["messages"]
                                )
                                if analysis["alerts"]["messages"]
                                else None,
                            }
                        )

                        st.markdown("---")
                        display_recommendations(analysis)

    with tab3:
        st.header("📜 Historical Records")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sensor Data History")
            limit = st.number_input("Number of records", 5, 100, 20)

            history_response = make_api_request(
                f"/api/sensor-data/latest?limit={limit}"
            )

            if history_response:
                df = pd.DataFrame(history_response)
                df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime(
                    "%Y-%m-%d %H:%M"
                )
                st.dataframe(
                    df[
                        [
                            "timestamp",
                            "soil_moisture",
                            "temperature",
                            "humidity",
                            "location",
                        ]
                    ],
                    use_container_width=True,
                )
            else:
                st.info("No historical data available.")

        with col2:
            st.subheader("Recommendation History")

            rec_history = make_api_request(f"/api/recommendations/latest?limit={limit}")

            if rec_history:
                df = pd.DataFrame(rec_history)
                df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime(
                    "%Y-%m-%d %H:%M"
                )
                st.dataframe(
                    df[
                        [
                            "timestamp",
                            "irrigation_action",
                            "fertilizer_action",
                            "alert_level",
                        ]
                    ],
                    use_container_width=True,
                )
            else:
                st.info("No recommendation history available.")


if __name__ == "__main__":
    main()
