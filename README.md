# Orientation Tracking

## Introduction
This project looks to  

## Environment

## Running Code
To start off, copy files and cd into that folder. Then, run:
```
pip install -r requirements.txt
```
This will install all the libraries needed to run the code locally. 

After this, open the .py file. Start with setting the dataset # to have the right dataset. Specify has_image = True if you want to get the panorama image as well. Go down to line 165. I have set the default pos (representing the number of values used to calculate biases and scale factors) as 300. Change as desired. In line 319, update alpha and max_iterations as desired. Save file and in terminal run the following command: 

```
python get_rotations.py
```

A csv file called final_estimates will include the q0:T values, while rotated_image_coordinates.csv will be the RGB values of the panorama image.
To convert the panorama image coordinates from 2D (Csv) back to 3D, run: 
```
array = np.loadtxt("rotated_image_coordinates.csv", delimiter=",")
array = array.reshape(1080, 1920, 3)
```
