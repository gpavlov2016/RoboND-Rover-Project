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

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 


---

### Sample images from simulator

![alt text][image1]

![alt text][image2]

### Autonomous Navigation and Mapping

The perception pipeline is as follows:
* Perspective transform - the image is modified to appear from a birds veiw perspective using openCV getPerspectiveTransform and warpPerspective methods.
* Color thresholding to detect three types of terrain:
  ** Navigable terrain - usually brighter than other types
  ** Non-navigable terrain - usually darker than the navigable or rocks
  ** Rocks - appear in golden shades
* Rover-to-world coordinate map conversion to align the classified terrain image with world map.
* Cartezian-to-polar coordinate converstion to aid the decision methods with average calculations.
The decision logic is based on a state machine with 3 modes:
* Forward - the rover sees navigable terrain and drivers forward towards the average angle of navigable terrain
* Stop - the rover reached the end of navigable terrain going forward and will turn around until it sees enough navigable terrain
* Stuck - the rover sees navigable terrain but can not move forward. In this case it will randomly rotate 90 degrees clock-wise or counter-clock-wise

#### Next steps  
For further improvement the decision logic can be augmented to use already visited point as a heuristic where to go, in addition the unstuck method can be improved to make more educated guesses instead of random turning 90 degrees.

![alt text][image3]

