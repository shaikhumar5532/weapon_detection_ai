# MATRIX WEAPON DETECTION SYSTEM  
### Real-Time Weapon Detection using YOLOv8 + Python + Tkinter

A futuristic Matrix-themed desktop application that detects weapons from **images**, **videos**, and **webcam live feed** using a trained **YOLOv8 object detection model**.

---

## Project Summary
This project demonstrates AI-powered real-time weapon detection using YOLOv8.  
It includes:

- Image detection  
- Video detection  
- Live webcam detection  
- Matrix UI theme   
- Weapon alerts + confidence score  
- System log with thumbnails  
- Multithreading for smooth UI  

---

## Detected Weapon Classes

| Class ID | Weapon  |
|----------|---------|
| 0        | Grenade |
| 1        | Knife   |
| 2        | Missile |
| 3        | Pistol  |
| 4        | Rifle   |

---

## Features

### 1. Image Detection
- Upload an image  
- YOLO highlights weapons  
- AI generates thumbnail preview  
- Confidence score visible  
- Beep alert on detection  

---

### 2. Video Detection
- Supports `.mp4`, `.mkv`, `.avi`, `.mov`  
- Frame-by-frame real-time processing  
- No UI freeze (threaded)  
- Auto-logs detections  
- Stops cleanly when video ends  

---

### 3. Webcam Detection
- Real-time scanning  
- Live detection panel  
- Alerts + thumbnails  
- Smooth experience using threads  

---

### 4. STOP FEED
Stops:

- Webcam detection  
- Video feed detection  

Ensures safe thread termination.

---

### 5. Matrix-Themed UI
- Hacker-like neon green theme  
- Animated scanning loader  
- Real-time system log  
- Cyberpunk thumbnails  
- Smooth UI animations  

