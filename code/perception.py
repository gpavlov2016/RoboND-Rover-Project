import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    #print('xpos, ypos: ', xpos, ypos)
    # Calculate pixel positions with reference to the rover position being at the
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel

# Clears pixels in img based on xpix and ypix
# xpix and ypix are in rover coordinates, first convert them
def mask_img(img, xpix, ypix):
    outimg = np.copy(img) #160x320
    x_pixel = np.clip(img.shape[1] - np.absolute(img.shape[0] + ypix).astype(np.int), 0, img.shape[1] - 1)
    y_pixel = np.clip((img.shape[0]-xpix).astype(np.int), 0, img.shape[0] - 1)
    #print('x_pixel, y_pixel: ', x_pixel, y_pixel)
    #boutimg[0:160, 0:320] = 0
    #xpixel = np.arange(40, 100)
    #ypixel = np.arange(40, 100)
    #print(sum(outimg[y_pixel, x_pixel]))
    outimg[y_pixel, x_pixel] = 100
    #print(sum(outimg[y_pixel, x_pixel]))
    return outimg

# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    # Apply a rotation
    # yaw angle is recorded in degrees so first convert to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = xpix * np.cos(yaw_rad) + ypix * np.sin(yaw_rad)
    ypix_rotated = xpix * np.sin(yaw_rad) + ypix * np.cos(yaw_rad)
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    # Perform translation and convert to integer since pixel values can't be float
    xpix_translated = np.int_(xpos + (xpix_rot / scale))
    ypix_translated = np.int_(ypos + (ypix_rot / scale))
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

def world_to_rover(xpix, ypix, xpos, ypos, yaw, scale):
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix, ypix, -xpos, -ypos, scale)
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix_tran, ypix_tran, -yaw)
    # Return the result
    return xpix_rot.astype(np.int), ypix_rot.astype(np.int)


# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped

def detect_obstacles(img, rgb_thresh_max = (160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    binimg = np.zeros_like(img[:,:,0])

    below_thresh = (img[:,:,0] < rgb_thresh_max[0]) \
                & (img[:,:,1] < rgb_thresh_max[1]) \
                & (img[:,:,2] < rgb_thresh_max[2])
    # Index the array of zeros with the boolean array and set to 1
    binimg[below_thresh] = 1
    # Return the binary image
    return binimg

def detect_rock(img):
    # Create an array of zeros same xy size as img, but single channel
    binimg = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    rgb_thresh_min = (110, 110, 5)
    rgb_thresh_max = (255, 255, 90)
    above_thresh = (img[:,:,0] > rgb_thresh_min[0]) \
                & (img[:,:,1] > rgb_thresh_min[1]) \
                & (img[:,:,2] > rgb_thresh_min[2])
    below_thresh = (img[:,:,0] < rgb_thresh_max[0]) \
                & (img[:,:,1] < rgb_thresh_max[1]) \
                & (img[:,:,2] < rgb_thresh_max[2])
    # Index the array of zeros with the boolean array and set to 1
    binimg[above_thresh & below_thresh] = 1
    # Return the binary image
    return binimg

# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # NOTE: camera image is coming to you in Rover.img
    #Rover.worldvisited[int(Rover.pos[0])-2:int(Rover.pos[0])+2, int(Rover.pos[1])-2:int(Rover.pos[1])+x2] = 1

    # 1) Define source and destination points for perspective transform
    # Define calibration box in source (actual) and destination (desired) coordinates
    # These source and destination points are defined to warp the image
    # to a grid where each 10x10 pixel square represents 1 square meter
    # The destination box will be 2*dst_size on each side
    dst_size = 5
    # Set a bottom offset to account for the fact that the bottom of the image
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 6
    img = Rover.img
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[img.shape[1] / 2 - dst_size, img.shape[0] - bottom_offset],
                              [img.shape[1] / 2 + dst_size, img.shape[0] - bottom_offset],
                              [img.shape[1] / 2 + dst_size, img.shape[0] - 2 * dst_size - bottom_offset],
                              [img.shape[1] / 2 - dst_size, img.shape[0] - 2 * dst_size - bottom_offset],
                              ])

    # 2) Apply perspective transform
    warped = perspect_transform(img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable_bin_img = color_thresh(warped)
    rock_bin_img = detect_rock(warped)
    obstacle_bin_img = detect_obstacles(warped)
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:, :, 0] = obstacle_bin_img*255
    Rover.vision_image[:, :, 1] = rock_bin_img*255
    Rover.vision_image[:, :, 2] = navigable_bin_img*255
    # 5) Convert map image pixel values to rover-centric coords
    xobst, yobst = rover_coords(obstacle_bin_img)
    xrock, yrock = rover_coords(rock_bin_img)
    xnav, ynav = rover_coords(navigable_bin_img)
    #print('xpix, ypix: ',xpix, ypix, len(xpix))
    # 6) Convert rover-centric pixel values to world coordinates
    obstacle_x_world, obstacle_y_world = pix_to_world(xobst, yobst, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], 10)
    nav_x_world, nav_y_world = pix_to_world(xnav, ynav, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], 10)
    rock_x_world, rock_y_world = pix_to_world(xrock, yrock, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], 10)
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    #print('obstacle_x_world, obstacle_y_world: ', obstacle_x_world, obstacle_y_world)
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    print('roll, pitch: ', Rover.roll, Rover.pitch)
    if (Rover.roll > 359 or Rover.roll < 1) and \
        (Rover.pitch < 1 or Rover.pitch > 359):
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += (
        1 & (Rover.worldmap[obstacle_y_world, obstacle_x_world, 2] == 0))
        Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        Rover.worldmap[nav_y_world, nav_x_world, 2] += 1
        Rover.worldmap[nav_y_world, nav_x_world, 0] = 0
    #print('xvisited, yvisited: ', xvisited, yvisited, len(xvisited))
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    #xnew = xpix
    #ynew = ypix
    #A = np.array([xpix,ypix])
    #B = np.array([xvisited,yvisited])

    '''
    for i in range(len(xpix)):
        for j in range(len(xvisited)):
            if xpix[i] == xvisited[j] and ypix[i] == yvisited[j]:
                xnew[i] = 0
                ynew[i] = 0
    '''

    #newpoints = A[np.all(np.any((A - B[:, None]), axis=2), axis=0)]

    '''
    x_world_visited, y_world_visited = Rover.worldmap[:, :, 2].nonzero()
    # Convert world to rover:
    x_rover_visited, y_rover_visited = \
        world_to_rover(x_world_visited, y_world_visited, Rover.pos[0], Rover.pos[1], Rover.yaw,  10)
    print('x_rover_visited, y_rover_visited: ', x_rover_visited, y_rover_visited)
    print('xnav, ynav: ', xnav, ynav)
    '''
    #print('Rover.worldvisited[nav_y_world, nav_x_world] > 0: ', Rover.worldvisited[nav_y_world, nav_x_world] > 0)
    #print('visit: ',  Rover.worldvisited[nav_x_world, nav_y_world])
    xnew = []
    ynew = []
    for i in range(len(nav_x_world)):
        if Rover.worldvisited[nav_y_world[i], nav_x_world[i]] == 0:
            xnew.append(xnav[i])
            ynew.append(ynav[i])
    #yvisited = Rover.worldvisited[nav_y_world, nav_x_world] > 0].astype(np.int)
    #print('xvisited, yvisited: ', xvisited, yvisited)
    print('xnew, ynew: ', xnew, ynew)
    print('len(xnew), len(xnav): ', len(xnew), len(xnav))

    #np.setdiff1d(np.transpose([xpix, ypix]), np.transpose([xvisited, yvisited]))
    #print('xnew, ynew: ', xnew, ynew)
    #if rock is found then go for it, else go according to navigable terrain
    Rover.rock_dists, Rover.rock_angles = to_polar_coords(xrock, yrock)
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(xnav, ynav)
    #Rover.vision_image = mask_img(Rover.vision_image, xnew, ynew)
    #print(xvisited, yvisited)
    #Rover.vision_image[xvisited, yvisited] = 0
    
    return Rover