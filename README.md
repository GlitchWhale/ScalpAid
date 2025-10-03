# Scalp Aid – Smart Scalp Health Monitoring Headband

## Overview
Scalp Aid is a college project focused on **preventing scalp issues** such as traction alopecia, dry skin, and overheating by using a smart wearable headband.  
The device monitors **scalp moisture, temperature, and tension** using sensors connected to a Raspberry Pi. Data is sent to a companion app that provides feedback, alerts, and suggestions to promote long-term scalp health.

---

## Features
- **Moisture Monitoring** – Detects scalp dryness and sweating patterns.
- **Temperature Monitoring** – Tracks scalp temperature to prevent overheating or dryness.
- **Tension Monitoring** – Monitors tight hairstyles and headwear to prevent traction alopecia.
- **Real-time Alerts** – Sends notifications when thresholds are exceeded.
- **Companion App** – Provides a user-friendly interface for data visualization and recommendations.

---

## Project Roles

### 👩‍🔧 Bianca Valicec – Hardware
- Research and selection of feasible sensors (moisture, temperature, tension).
- Hardware prototyping with Raspberry Pi and sensor integration.
- Building the headband and ensuring comfort + functionality.

### 🗄️ Priyanka Achoki – Database
- Designing and managing the database structure for storing sensor readings.
- Ensuring reliable data handling between Raspberry Pi and app.
- Setting up secure data storage and retrieval mechanisms.

### 🧪 Innocencia Chauke – Software Testing
- Writing and executing test plans for the app and hardware interactions.
- Ensuring software reliability and usability.
- Verifying that sensor readings are accurate and alerts trigger correctly.

### 🎨 Diana Aboa – Front End
- Designing the companion app’s user interface.
- Implementing data visualization (graphs, alerts, dashboards).
- Focusing on usability, accessibility, and clear communication of scalp health status.

---

## Technology Stack
- **Hardware:** Raspberry Pi + selected sensors (GSR, DS18B20, FSR/stretch sensor).
- **Software:** Python for data collection, custom app for front end.
- **Database:** SQL/NoSQL solution for storing sensor data.
- **Frontend:** Web/mobile app (to display scalp condition and alerts).

---

## Goals
1. Prototype a functional wearable that measures scalp conditions in real-time.
2. Provide an app interface that makes data accessible and actionable.
3. Raise awareness of scalp health and provide preventive solutions.
