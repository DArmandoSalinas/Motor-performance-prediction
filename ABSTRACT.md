# Abstract

This project presents a real-time Motor Preventive Monitoring System for Sumitomo 3-phase induction motors, enabling predictive maintenance through continuous health assessment. The system integrates ADXL355 3-axis accelerometer and MLX90614 infrared temperature sensors with an ESP32 microcontroller, acquiring vibration and temperature data at 10 Hz. A Python-based software architecture processes sensor data using statistical analysis and rule-based anomaly detection to compute interpretable health scores (0-100).

The system implements multi-speed baseline profiling for five operating speeds (50%, 60%, 75%, 90%, 100%), utilizing Z-score analysis for vibration and absolute temperature limits to provide color-coded status indicators with diagnostic messages. A premium web-based dashboard built with Streamlit and Plotly delivers real-time visualizations including health gauges, time-series plots, and statistical distributions.

Featuring a multi-threaded architecture with robust error handling and auto-reconnection, the system achieves 5-10 FPS UI refresh rates with sub-5ms analysis latency, demonstrating production-ready performance for industrial predictive maintenance applications.

---

## Project Objectives

### Primary Objectives

1. **Develop a Real-Time Monitoring System**
   - Design and implement a continuous monitoring system capable of acquiring vibration and temperature data from industrial motors at 10 Hz sampling rate
   - Ensure real-time data processing with minimal latency (<5ms) for immediate health assessment

2. **Implement Multi-Speed Baseline Profiling**
   - Create statistical baseline profiles for five different motor operating speeds (50%, 60%, 75%, 90%, 100%)
   - Establish normal operating parameters for each speed profile to enable accurate anomaly detection

3. **Design Interpretable Anomaly Detection**
   - Develop rule-based algorithms using statistical analysis (Z-scores) for vibration anomaly detection
   - Implement absolute temperature limits for thermal anomaly detection
   - Ensure all health assessments are interpretable and explainable (no black-box machine learning)

4. **Create Health Scoring System**
   - Design a 0-100 health scoring algorithm that maps sensor deviations to intuitive health metrics
   - Implement color-coded status indicators (Normal/Caution/Danger) for quick visual assessment
   - Generate human-readable diagnostic messages explaining system status

5. **Build Premium User Interface**
   - Develop a modern, intuitive web-based dashboard using Streamlit and Plotly
   - Implement real-time visualizations including health gauges, time-series plots, 3D vibration vectors, and statistical distributions
   - Ensure responsive design with 5-10 FPS refresh rates for smooth user experience

### Secondary Objectives

6. **Ensure System Robustness**
   - Implement multi-threaded architecture to prevent UI freezing during data acquisition
   - Develop robust error handling with automatic reconnection capabilities
   - Create data validation mechanisms to filter invalid sensor readings

7. **Enable Testing and Development**
   - Implement data replay mode for testing without live hardware
   - Support adjustable playback speeds for flexible testing scenarios
   - Provide comprehensive documentation for system understanding and maintenance

8. **Achieve Production-Ready Performance**
   - Optimize system performance to handle continuous operation
   - Ensure efficient memory management with fixed-size buffers
   - Validate system reliability through extended operation testing

### Expected Outcomes

- A fully functional real-time motor health monitoring system
- Early detection of motor anomalies before catastrophic failure
- Reduced maintenance costs through predictive maintenance approach
- Improved motor reliability and operational efficiency
- User-friendly interface accessible to non-technical operators
- Comprehensive documentation for system deployment and maintenance
