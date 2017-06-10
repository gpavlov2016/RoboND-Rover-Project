import numpy as np

speed_history = []
last_stop = 0
'''

def world_to_rover(xpix, ypix, xpos, ypos, yaw, scale)
    # Apply rotation
    xpix_rot, ypix_rot = percepion.rotate_pix(xpix, ypix, -yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, -xpos, -ypos, scale)
    # Return the result
    return xpix_tran, ypix_tran
def yaw_decision(Rover):
    aavg = np.mean(Rover.nav_angles * 180 / np.pi)
    # get all visited locations from the map
    #x_world_visited = xpix[Rover.worldmap[x_pix_world, y_pix_world, 2] > 100].astype(np.int)
    #y_world_visited = ypix[Rover.worldmap[x_pix_world, y_pix_world, 2] > 100].astype(np.int)
    # Identify nonzero pixels
    x_world_visited, y_world_visited = Rover.worldmap[:, :, 2].nonzero()
    #print('xpos, ypos: ', xpos, ypos)
    # Calculate pixel positions with reference to the rover position being at the
    # center bottom of the image.
    x_rover = world_to_rover(x_world_visited, y_world_visited, Rover.xpos, Rov.ypos, Rover.yaw, )
    y_rover = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel
'''

def angle_close(angle, target, thresh = 5):

    if angle > target - thresh and angle < target + thresh:
        return True
    else:
        return False

def unstuck(Rover):
    print('stuck:', Rover.yaw, Rover.target_yaw)

    # If we're in stop mode but still moving keep braking
    if abs(Rover.vel) > 0:
        Rover.throttle = 0
        Rover.brake = Rover.brake_set
        Rover.steer = 0
    # If we're not moving (vel < 0.2) then do something else
    # elif Rover.vel <= 0.2:
    elif not angle_close(Rover.yaw, Rover.target_yaw):
        Rover.throttle = 0
        # Release the brake to allow turning
        Rover.brake = 0
        # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
        Rover.steer = Rover.turn_direction  # Could be more clever here about which way to turn
    else:
        Rover.throttle = Rover.throttle_set
        Rover.mode = 'forward'
        # Release the brake
        Rover.brake = 0
        Rover.steer = 0
        Rover.stuck_cnt = 0

    return  Rover

def normalize_angle_deg(angle):
    if angle > 0 and angle < 360:
        return angle
    elif angle < 0:
        return angle + 360
    else:
        return angle - 360

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    speed_history.append(Rover.vel)
    global last_stop
    Rover.cnt += 1

    import random

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        print('Rover.mode: ', Rover.mode)
        # Check for Rover.mode status
        if Rover.mode == 'stuck':
            return unstuck(Rover)

        if len(Rover.rock_angles) > 0:
            turn_angle = np.mean(Rover.rock_angles * 180 / np.pi)
        else:
            turn_angle = np.mean(Rover.nav_angles * 180 / np.pi) + 5

        if Rover.mode == 'forward':
            if Rover.cnt % 240 == 0:
                Rover.turn_direction = random.choice([-15, 15])

            print('Rover.stuck_cnt: ', Rover.stuck_cnt)
            if (abs(Rover.vel) < 0.1 and abs(Rover.throttle) > 0):
                Rover.stuck_cnt += 1
                if Rover.stuck_cnt > 20:
                    Rover.mode = 'stuck'
                    Rover.stuck_cnt = 0
                    Rover.target_yaw = normalize_angle_deg(Rover.yaw + random.choice([-1, 1])*90)
                    if Rover.target_yaw < Rover.yaw:
                        Rover.turn_direction = 15
                    else:
                        Rover.turn_direction = -15
                    print('Rover.target_yaw: ', Rover.target_yaw)
            else:
                last_stop = 0
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(turn_angle, -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            #elif Rover.vel <= 0.2:
            else:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = Rover.turn_direction # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    # if angle is not too sharp move forward, otherwise turn in place
                    if (turn_angle > -15 and turn_angle < 15):
                        Rover.throttle = Rover.throttle_set
                        Rover.mode = 'forward'
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(turn_angle, -15, 15)
    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.mode = 'stop'
        Rover.throttle = 0
        Rover.steer = 0
        Rover.brake = Rover.break_set

    if Rover.picking_up and Rover.near_sample:
        return Rover

    if Rover.near_sample and not Rover.picking_up:
        Rover.throttle = 0
        Rover.brake = Rover.brake_set

        # pick up the rock
        if Rover.vel == 0:
            Rover.send_pickup = True
    return Rover

