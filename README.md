# Parallelized Deep Convolutional Neural Networks for Pathology Detection and Localization in Chest X-Rays

_This repository contains the code for the prototype application I developed for the Final Research Project of the
**BSc. (Hons.) in Computer Science** degree at University of Westminster (taught at IIT Sri Lanka)_

## Project Introduction

Radiography is a prevalent method of medical diagnosis, especially in humans. Out of the various types of Radiography,
Chest Radiography holds an important place due to the numerous diseases diagnosed through it. These diseases vary from
low-risk diseases to high-risk, life-threatening diseases. Due to this, accurate diagnosis of Chest X-Rays is considered
very crucial. This research project presents a novel way of utilizing multiple Convolutional Neural Networks for
accurate detection and localization of diseases present in Chest X-Ray images. The proposed algorithm creates a range of
new pathways to conduct research in a variety of fields and use cases. The research also aims to prove the proposed
algorithm's strengths and advantages for Chest X-Ray classification within a well-defined scope.

## Project Pitch

[![PROJECT PITCH](https://img.youtube.com/vi/0PmXOY-Mt1k/0.jpg)](https://www.youtube.com/watch?v=0PmXOY-Mt1k)

## Full Project Demonstration

[![PROJECT DEMO](https://img.youtube.com/vi/SBVE1NVDHcA/0.jpg)](https://www.youtube.com/watch?v=SBVE1NVDHcA)

## Technologies

Following are the main technologies used in this project

- Python
- TensorFlow, Keras
- Numpy
- Flask
- HTML5, CSS, JS

## Application Installation

### 1. Pre-requisites

    - Python 3.7+
    - PIP
    - CUDA supported GPU with at least 10GB VRAM
        - CUDA installation

### 2. Install Dependencies

   ```
   pip install -r requirements.txt
   ```

### 3. Place the model files

- Place the model files in their respective folders

### 4. Running the Application

```
python3 app.py --host=0.0.0.0 --port=5000 --cert=adhoc --no-reload
```

After the execution of this line you can visit you localhost to visit the application

## Model Accuracy

[TODO]

## Acknowledgements

We acknowledge below experts for the contribution of their valuable knowledge throughout this project

- Dr. Nilmini Fernando (MBBS, DFM)
- Dr. Harshana Bandara (MBBS, MD)
- Dr. Prasantha De Silva (MBBS, MSc)