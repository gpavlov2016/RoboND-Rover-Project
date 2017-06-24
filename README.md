## Project: Search and Sample Return

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

[//]: # (Image References)

[image1]: ./misc/example_grid1.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 
[image4]: ./calibration_images/persp.jpg 
[image5]: ./calibration_images/bin.jpg 
[image6]: ./calibration_images/mosaic.jpg 

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

### Notebook Analysis
#### The rover simulator sumulates "Martian" terrain with three main areas in the image - navigable terrain, non-navigable terrain and rocks. Here is an example of an image captured from the sumulator:

![alt text][image1]

#### Image Processing pipeline
* Perspective transform - the image is modified to appear from a birds veiw perspective using openCV getPerspectiveTransform and warpPerspective methods.

![The resulting image after applying perspecive transform][image4]

* Color thresholding to detect three types of terrain:
  ** Navigable terrain - this area is usually brighter than other area types therefore the filtering is achieved by color thresholding in the RGB space above the values (160, 160, 160). The task is handled by the function color_thresh()
  ** Non-navigable terrain - usually darker than the navigable area or rocks therefore filtering is done by taking the pixels below the value (160, 160, 160) which is the complement in RGB space to the navigable terrain pixels. For readability the task is handled in a separate function detect_obstacles()
  ** Rocks - those are tiny pieces of the image that usaully appear in a navigable terrain but have distinct golden color. To detect them the function detect_rock() uses yellow color range in RGB space as follows:
    rgb_thresh_min = (110, 110, 5)
    rgb_thresh_max = (255, 255, 90)

![Example of rock][image3]


![The resulting image after applying the binarization based on Navigble Terrain color thresholding][image5]
  
* Rover-to-world coordinate map conversion to align the classified terrain image with world map.
* Cartezian-to-polar coordinate converstion to aid the decision methods with average calculations.

![Visualization of the pipeline after applying each step to the image. The red arrow in the right bottom image shows the average angle of navigable terrain in rover polar coordinates
][image6]

The decision logic is based on a state machine with 3 modes:
* Forward - the rover sees navigable terrain and drives forward towards the average angle of navigable terrain
* Stop - the rover reached the end of navigable terrain going forward and will turn around until it sees enough navigable terrain
* Stuck - the rover sees navigable terrain but can not move forward. In this case it will randomly rotate 90 degrees clock-wise or counter-clock-wise

#### Next steps  
For further improvement the decision logic can be augmented to use already visited point as a heuristic where to go, in addition the unstuck method can be improved to make more educated guesses instead of random turning 90 degrees.


