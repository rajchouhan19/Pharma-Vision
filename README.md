````md
# Pharma Vision – AI-Based Tablet & Capsule Inspection System

Pharma Vision is a computer vision-based medicine inspection system developed to detect defective tablets and capsules during conveyor belt movement. The project aims to automate medicine quality inspection in pharmaceutical manufacturing by identifying damaged medicines such as broken tablets and open/broken capsules.

The system supports both **image and video inspection** using computer vision techniques. A Flask-based web application is integrated where users can upload medicine images or conveyor videos for real-time quality inspection.

## Features

- Tablet defect detection using shape analysis
- Capsule defect detection for broken/open capsules
- Conveyor video inspection support
- Bounding box visualization
- PASS/FAIL inspection status
- Flask-based web interface
- Image and video upload support

## Project Preview

| Home Page | Tablet Detection |
|------------|------------------|
| ![](assets/home_page.png) | ![](assets/tablet_result.png) |

| Capsule Detection | Video Inspection |
|-------------------|------------------|
| ![](assets/capsule_result.png) | ![](assets/video_result.png) |

## Tech Stack

- Python
- OpenCV
- NumPy
- Flask
- Computer Vision

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
└── requirements.txt
````

## Installation

Clone the repository:

```bash
git clone https://github.com/rajchouhan19/Pharma-Vision.git
```

Move to project folder:

```bash
cd Pharma-Vision
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

## Future Improvements

* Deep Learning-based defect detection (YOLO)
* Real-time live camera inspection
* Better defect classification
* Production-scale conveyor integration

## Author

Raj Narayan Singh Chouhan

```
```
