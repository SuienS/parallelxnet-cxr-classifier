# Parallelized Deep Convolutional Neural Networks for Pathology Detection and Localization in Chest X-Rays

_This repository contains the code for the prototype application I developed for the Final Research Project of the
**BSc. (Hons.) in Computer Science** degree at University of Westminster (taught at IIT Sri Lanka)_

## Authors

- [Ravidu Silva](mailto:ravidus.ac@gmail.com)
- [Pumudu Fernando (Supervisor)](mailto:pumudu.f@iit.ac.lk)

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

### 3. Model file placement

- Place the model files in their respective folders

### 4. Running the Application

```
python3 app.py --host=0.0.0.0 --port=5000 --cert=adhoc --no-reload
```

After the execution of this line you can visit you localhost to use the application

## Model Accuracy

### Models Names

- R-50v2: ResNet50v2
- D-121: DenseNet-121
- D-169: DenseNet-169
- R-D-Ens: Ensemble of ResNet50v2, DenseNet-121 and DenseNet-169
- P-64: ParallelXNet (ratio: 64)
- P-128: ParallelXNet (ratio: 128)
- P-Ens: Ensemble of P-64 and P-128

### Test results on MIMIC-CXR 2020

|Model \Pathology|R-50v2|D-121|D-169|R-D-Ens|P-64|P-128|P-Ens|
|:--------------:|:------:| :-----:| :-----:| :-----:| :-----:| :-----:| :-----:|
|Enlarged Cardiom.|0.7026|0.7048|**0.7209**|0.7159|0.7061|0.7076|0.7107|
|Cardiomegaly|0.7808|0.7807|0.7888|0.7889|0.7921|0.7874|**0.7932**|
|Lung Lesion|0.6965|0.7053|0.7111|0.7109|0.7155|0.7157|**0.7192**|
|Lung Opacity|0.6899|0.6946|0.6967|0.7000|0.6978|0.7007|**0.7031**|
|Edema|0.8357|0.8389|**0.8434**|0.8432|0.8403|0.8391|0.8419|
|Consolidation|0.7475|0.7507|0.7548|0.7580|**0.7605**|0.7514|0.7597|
|Pneumonia|0.7116|0.7228|0.7289|0.7302|0.7341|0.7303|**0.7372**|
|Atelectasis|0.7634|0.7627|0.7668|0.7688|0.7674|0.7680|**0.7703**|
|Pneumothorax|0.8467|0.8691|0.8640|0.8690|0.8595|**0.8711**|0.8706|
|Pleural Effusion|0.8897|0.8921|0.8941|0.8957|0.8971|0.8952|**0.8985**|
|Pleural Other|0.8067|0.8255|**0.8544**|0.8396|0.8313|0.8504|0.8466|
|Fracture|0.6613|**0.6944**|0.6894|0.6891|0.6933|0.6810|0.6916|
|Support Devices|0.8661|0.8994|0.9029|0.9041|0.9039|0.9070|**0.9085**|

- ‘ParallelXNet’ is better at **9 out of 13** labels of the dataset.

### Test results on ChestX-ray-14

|Pathology \Model|R-50v2  |D-121   |D-169   |R-D-Ens |P-64    |P-128   |P-Ens   |
|:--------------:|:------:| :-----:| :-----:| :-----:| :-----:| :-----:| :-----:|
|Nodule|0.7585|0.7736|0.7762|0.7817|0.7826|0.7807|**0.7875**|
|Cardiomegaly|0.8770|0.8876|0.8873|0.8943|0.8901|0.8927|**0.8958**|
|Emphysema|0.9098|0.9276|0.9259|0.9288|0.9294|0.9312|**0.9335**|
|Fibrosis|0.8183|0.8257|0.8359|0.8355|0.8321|0.8344|**0.8381**|
|Edema|0.8397|0.8489|0.8471|0.8522|0.8502|0.8474|**0.8526**|
|Consolidation|0.7389|0.7443|0.7505|0.7531|0.7529|0.7527|**0.7576**|
|Pneumonia|0.7137|0.7287|0.7351|0.7337|0.7386|0.7353|**0.7411**|
|Atelectasis|0.7741|0.7799|0.7807|0.7868|0.7863|0.7823|**0.7888**|
|Pneumothorax|0.8649|0.8730|0.8733|**0.8787**|0.8720|0.8740|0.8773|
|Effusion|0.8248|0.8338|0.8343|0.8376|0.8359|0.8370|**0.8399**|
|Mass|0.8128|0.8342|0.8259|0.8361|0.8329|0.8414|**0.8433**|
|Infiltration|0.6895|0.7013|0.7031|**0.7047**|0.6984|0.7028|0.7041|
|Hernia|0.8703|0.8767|0.8847|0.8880|0.8742|0.8905|**0.8911**|
|Pleural Thickening|0.7742|0.7899|0.7918|**0.7949**|0.7897|0.7889|0.7942|

- ‘ParallelXNet’ is better at **11 out of 14** labels of the dataset.

## Acknowledgements

We acknowledge below experts for the contribution of their valuable knowledge throughout this project

- Dr. Nilmini Fernando (MBBS, DFM)
- Dr. Harshana Bandara (MBBS, MD)
- Dr. Prasantha De Silva (MBBS, MSc)