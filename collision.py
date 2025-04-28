import math

import math

def resolve_ball_obj_collision(circle_pos, circle_vel, radius, rect, bounce_factor):
    # Find the closest point on the rectangle to the ball's center
    closest_x = max(rect.left, min(circle_pos[0], rect.right))
    closest_y = max(rect.top, min(circle_pos[1], rect.bottom))
    dx = circle_pos[0] - closest_x
    dy = circle_pos[1] - closest_y
    distance = math.hypot(dx, dy)

    # If the ball is colliding with the rectangle
    if distance < radius:
        if distance == 0:
            distance = 0.1  # Avoid division by zero if the ball is exactly at the corner

        # Normalize the collision normal (direction)
        nx, ny = dx / distance, dy / distance
        
        # Calculate the overlap distance
        overlap = radius - distance

        # Move the ball outside the rectangle by the overlap distance
        circle_pos[0] += nx * overlap
        circle_pos[1] += ny * overlap
        
        # Ensure the ball's velocity is adjusted correctly along the collision normal
        # Project the velocity onto the normal direction (nx, ny)
        velocity_normal = circle_vel[0] * nx + circle_vel[1] * ny
        circle_vel[0] -= 2 * velocity_normal * nx  # Reflect the velocity along the normal
        circle_vel[1] -= 2 * velocity_normal * ny

        # Apply the bounce factor to adjust the velocity's magnitude
        circle_vel[0] *= bounce_factor
        circle_vel[1] *= bounce_factor


import math

def resolve_ball_player_collision(circle_pos, circle_vel, radius, rect, bounce_factor):
    # Find the closest point on the rectangle to the ball's center
    closest_x = max(rect.left, min(circle_pos[0], rect.right))
    closest_y = max(rect.top, min(circle_pos[1], rect.bottom))
    dx = circle_pos[0] - closest_x
    dy = circle_pos[1] - closest_y
    distance = math.hypot(dx, dy)

    # If the ball is colliding with the rectangle
    if distance < radius:
        if distance == 0:
            distance = 0.1  # Avoid division by zero if the ball is exactly at the corner

        # Normalize the collision normal (direction)
        nx, ny = dx / distance, dy / distance
        
        # Calculate the overlap distance
        overlap = radius - distance

        # Move the ball outside the rectangle by the overlap distance
        circle_pos[0] += nx * overlap
        circle_pos[1] += ny * overlap
        
        # Ensure the ball's velocity is adjusted correctly along the collision normal
        # Project the velocity onto the normal direction (nx, ny)
        velocity_normal = circle_vel[0] * nx + circle_vel[1] * ny
        circle_vel[0] -= 2 * velocity_normal * nx  # Reflect the velocity along the normal
        circle_vel[1] -= 2 * velocity_normal * ny

        # Apply the bounce factor to adjust the velocity's magnitude
        circle_vel[0] *= bounce_factor
        circle_vel[1] *= bounce_factor

        # If the ball has no significant velocity, give it a small boost
        if math.hypot(circle_vel[0], circle_vel[1]) < 10:  # Check if the ball is nearly stationary
            # boost_magnitude = 10 # Adjust this value for the desired minimum speed boost
            circle_vel[0] += nx * 8  # Apply a small boost in the direction of the collision normal
            circle_vel[1] += ny * 10

