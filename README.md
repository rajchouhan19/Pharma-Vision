````md
# Pharma Vision – AI-Based Tablet & Capsule Inspection System

Pharma Vision is a computer vision-based medicine inspection system developed to detect defective tablets and capsules during conveyor belt movement. The goal of this project is to automate medicine quality inspection in pharmaceutical manufacturing by identifying damaged medicines such as broken tablets and open/broken capsules.

The system supports both **image and video inspection** through a simple **Flask-based web interface**, where users can upload medicine images or conveyor videos and get inspection results with defect detection, counts, and PASS/FAIL status.

---

## Features

- Tablet defect detection using shape analysis
- Capsule defect detection for broken/open capsules
- Conveyor belt video inspection support
- Image and video upload support
- Bounding box visualization for detected medicines
- PASS/FAIL inspection status
- Flask-based web interface

---

## Project Preview

### Home Page

<img src="assets/home_page.png" width="850">

### Tablet Inspection Result

<img src="assets/tablet_result.png" width="850">

### Capsule Inspection Result

<img src="assets/capsule_result.png" width="850">

---

## Tech Stack

- Python
- OpenCV
- NumPy
- Flask
- Computer Vision

---

## Project Structure

```bash
Pharma-Vision/
│── app.py
│
├── tablet/
│   └── tablet_processor.py
│
├── capsule/
│   └── capsule_processor.py
│
├── templates/
│   ├── index.html
│   └── result.html
│
├── static/
│   ├── style.css
│   ├── uploads/
│   └── outputs/
│
├── assets/
│   ├── home_page.png
│   ├── tablet_result.png
│   └── capsule_result.png
│
├── requirements.txt
│
└── README.md
````

---

## Installation

### Clone the repository

```bash
git clone https://github.com/rajchouhan19/Pharma-Vision.git
```

### Move to project folder

```bash
cd Pharma-Vision
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

### Open in browser

```text
http://127.0.0.1:5000
```

---

## Future Improvements

* Deep Learning-based defect detection (YOLO)
* Real-time live camera inspection
* Better defect classification
* Production-scale conveyor integration

---

## Author

**Raj Narayan Singh Chouhan**

```
```
