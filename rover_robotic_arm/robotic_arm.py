import math
import numpy as np
from random import randint

# NOTE: These functions can be added to a library - optional

# Vectorial Calculations
def sum_vector(v1, v2):
    v_t = [0, 0, 0]
    for i in range(3):
        v_t[i] = v1[i] + v2[i]
    return v_t
def RotZ(point, theta, is_theta_degrees = False):
    if (is_theta_degrees):
        theta_in_rad = math.radians(theta)
    else:
        theta_in_rad = theta

    rotZ_matrix = [ [math.cos(theta_in_rad), -math.sin(theta_in_rad), 0],
                    [math.sin(theta_in_rad), math.cos(theta_in_rad), 0],
                    [0, 0, 1]]
    result = [0, 0, 0]

    for i in range(0, 3):
        _sum = 0

        for j in range(0, 3):
            _sum += point[j] * rotZ_matrix[i][j]
        result[i] = _sum
    return result
def rotation_u(point_to_be_rotated, vector_rotating_around, angles_in_deg):
    u = vector_rotating_around
    if length(u) != 1:
        u = make_unit(u)
    p = point_to_be_rotated
    a = math.radians(angles_in_deg) # Convert to radians
    omc = 1 - math.cos(a)

    matrix = [
    [(math.cos(a) + u[0] * u[0] * omc), (u[0] * u[1] * omc - u[2] * math.sin(a)), (u[0] * u[2] * omc + u[1] * math.sin(a))],
    [(u[1] * u[0] * omc + u[2] * math.sin(a)), (math.cos(a) + u[1] * u[1] * omc), (u[1] * u[2] * omc - u[0] * math.sin(a))],
    [(u[0] * u[2] * omc - u[1] * math.sin(a)), (u[1] * u[2] * omc + u[0] * math.sin(a)), (math.cos(a) + u[2] * u[2] * omc)]
    ]

    result = [0, 0, 0]

    for i in range(0, 3):
        _sum = 0

        for j in range(0, 3):
            _sum += p[j] * matrix[i][j]
        result[i] = _sum

        # # 0.0001 is the maximum error
        # if (math.fabs(result[i]) < 0.0001):
        #     result[i] = 0

    return result
def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c
def angle(v1, v2, acute = True):
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    if (acute == True):
        return angle
    else:
        return 2 * np.pi - angle
def length(vector):
    return math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2) + math.pow(vector[2], 2))
def make_unit(vector):
    len_v = length(vector)
    return [vector[0] / len_v, vector[1] / len_v, vector[2] / len_v]
def scalar_of_vector(vector, scalar):
    return [vector[0] * scalar, vector[1] * scalar, vector[2] * scalar]
def subtract(vector1, vector2):
    return [vector1[0] - vector2[0], vector1[1] - vector2[1], vector1[2] - vector2[2]]

# Triangle Calculations
def cosine_rule(c, a, b):
    cos_theta = (-1 * ((c * c) - (b * b) - (a * a))) / (2 * a * b)
    return math.acos(cos_theta)
def get_triangle_angles(a, b, c):
    return [cosine_rule(a, b, c), cosine_rule(b, a, c), cosine_rule(c, a, b)]
def get_length_from_cos(a, b, theta_in_degrees):
    theta_rad = math.radians(theta_in_degrees)
    return math.sqrt(a * a + b * b - 2 * a * b * math.cos(theta_rad))

# Inverse Calculations
def geometric_approach(lengths, point):
    dist = length(point)
    angles = get_triangle_angles(lengths[0], lengths[1], dist)
    vector_plane_angle = math.asin(point[2] / dist)
    # To degrees Conversion
    vector_plane_angle = math.degrees(vector_plane_angle)
    for i in range(0, 3):
        angles[i] = math.degrees(angles[i])
    base_angle = vector_plane_angle + angles[1]
    joint2_angle = 180 - angles[2]
    base_rotation = math.degrees(math.atan2(point[1], point[0]))
    return [base_rotation, base_angle, joint2_angle]
def is_between(val, min, max):
    if val >= min and val <= max:
        return True
    else:
        return False

class RoverArm(object):
    def __init__(self, lengths):
        self.Lengths = lengths;
        self.limits = [[-50, 50], [10, 110], [20, 70], [0, 70], [0, 360]] # [base_yaw, base_pitch, secondary_axis, gripper_pitch, gripper_rotation]
        self.joint_names = ["base_yaw", "base_pitch", "secondary_axis", "gripper_pitch", "gripper_rotation"]
        self.last_point = [0, 0, 0]
        self.degrees_to_mm = True
        self.actuator_lengths = [0, 0]

    def check_limits(self, _joint_angles):
        for i in range(0, len(_joint_angles)):
            if not is_between(_joint_angles[i], self.limits[i][0], self.limits[i][1]):
                print "[ BOUNDS ERROR ] " + self.joint_names[i] + " angle({0}) is outside of bounds: ({1}, {2})".format(_joint_angles[i], self.limits[i][0], self.limits[i][1])
                # print "[ JOINT STATE CHANGE ] " + self.joint_names[i] + " angle has been changed to: {0}".format(_joint_angles[i])

    def print_cool_words(self):
        random1 = randint(4, 8)
        arr = []
        print "[ OK ] Joint Calculations Completed"
        arr.append("[ WARNING ] End-Point velocity has %{0} error".format(random1))
        arr.append("[ OK ] ")
        selector = randint(0, len(arr) - 1)

        print arr[selector]

    def update_destination_point(self, point, vector):
        if not length(vector) == 1:
            vector = make_unit(vector)
        last_joint_vector = scalar_of_vector(vector, self.Lengths[2])
        self.destination_point = point
        self.secondary_dest_point = subtract(point, last_joint_vector)
        self.direction_vector = vector
        geo = geometric_approach(self.Lengths, self.secondary_dest_point)
        v1 = rotation_u([self.Lengths[0], 0, 0], [0, -1, 0], geo[1])
        v1 = rotation_u(v1, [0, 0, 1], geo[0])
        v2 = subtract(self.secondary_dest_point, v1)
        last_angle = 180 - math.degrees(angle(vector, v2))
        first_pair_normal = cross(v2, vector)
        second_pair_normal = cross(v1, v2)
        add_axis = math.degrees(angle(first_pair_normal, second_pair_normal))
        self.joint_angles = [geo[0], geo[1], geo[2], last_angle, add_axis]
        v1 = scalar_of_vector(make_unit(v1), self.Lengths[0])
        v2 = scalar_of_vector(make_unit(v2), self.Lengths[1])
        v3 = scalar_of_vector(vector, self.Lengths[2])
        self.vectors = [v1, v2, v3]
        p1 = v1
        p2 = sum_vector(v1, v2)
        p3 = sum_vector(p2, v3)
        self.joint_points = [p1, p2, p3]

        # degrees to mm Conversion
        if self.degrees_to_mm:
            self.joint_angles[2] = get_length_from_cos(7.5, 32.7, self.joint_angles[2]) - self.actuator_lengths[1]
            self.joint_angles[1] = get_length_from_cos(10, 10, self.joint_angles[1]) - self.actuator_lengths[0]
            print self.joint_angles

        self.check_limits(self.joint_angles)
        
        # self.print_cool_words()
        # Calculation of the vectorial speed of joints
        w_rot_base = 1
        w_ab = 1
        w_bc = 1
        w_cd = 1
        w_additional = 1

        # vector orientation Calculation
        normal_1 = make_unit(cross(self.vectors[0], point))
        normal_2 = make_unit(cross(self.vectors[1], sum_vector(self.vectors[1], self.vectors[2])))
        velocity_1 = make_unit(cross(normal_1, point))
        velocity_2 = make_unit(cross(sum_vector(self.vectors[1], self.vectors[2]), normal_2))
        velocity_3 = make_unit(cross(normal_2, self.vectors[2]))
        velocity_4 = normal_2
        velocity_5 = normal_1

        vel_1_scalar = w_ab * length(point)
        vel_2_scalar = w_bc * length(sum_vector(self.vectors[1], self.vectors[2]))
        vel_3_scalar = w_cd * length(self.vectors[2])
        vel_4_scalar = w_additional * math.sin(math.radians(180 - self.joint_angles[3])) * self.Lengths[2]
        vel_5_scalar = w_rot_base * math.sqrt(point[0] * point[0] + point[1] * point[1])

        velocity_1 = scalar_of_vector(velocity_1, vel_1_scalar)
        velocity_2 = scalar_of_vector(velocity_2, vel_2_scalar)
        velocity_3 = scalar_of_vector(velocity_3, vel_3_scalar)
        velocity_4 = scalar_of_vector(velocity_4, vel_4_scalar)
        velocity_5 = scalar_of_vector(velocity_5, vel_5_scalar)

        self.velocity = [velocity_1, velocity_2, velocity_3, velocity_4, velocity_5]

        self.last_point = point

    def foward_model(self, angles):
        for i in range(1, len(angles) - 1):
            angles[i] = math.radians(angles[i])
        theta2_prime = math.radians(90) + angles[1] - angles[2]
        theta4_prime = math.radians(90) - (angles[3] - theta2_prime)

        p1 = [self.Lengths[0] * math.cos(angles[1]), 0, self.Lengths[0] * math.sin(angles[1])]
        p2 = [self.Lengths[1] * math.sin(theta2_prime), 0, -self.Lengths[1] * math.cos(theta2_prime)]
        p2 = sum_vector(p1, p2)
        p3 = [self.Lengths[2] * math.cos(theta4_prime), 0, self.Lengths[2] * math.sin(theta4_prime)]
        p3 = rotation_u(p3, subtract(p2, p1), -180 + angles[4])
        p3 = sum_vector(p2, p3)

        p1 = rotation_u(p1, [0,0,1], angles[0])
        p2 = rotation_u(p2, [0,0,1], angles[0])
        p3 = rotation_u(p3, [0,0,1], angles[0])

        return [p1, p2, p3]

    # NOTE: Returning format: "base_yaw,base_pitch,secondary_axis,gripper_pitch,gripper_rotation"
    def return_model(self):
        str_msg = ""
        for i in range(0, len(self.joint_angles) - 1):
            str_msg += str(self.joint_angles[i]) + str(",")
        str_msg += str(self.joint_angles[len(self.joint_angles) - 1])
        return str_msg

    def print_info(self):
        print "Destination Point: " + str(self.destination_point)
        print "Gripper Point: " + str(self.secondary_dest_point)
        print "Direction Vector: " + str(self.direction_vector)
        print "Segment Lengths: " + str(self.Lengths)
        print "Joint Angles[base_yaw, base_pitch, secondary_axis, gripper_pitch, gripper_rotation]: " + str(self.joint_angles)
        print "Segment Vectors: " + str(self.vectors)
        print "Joint Points: " + str(self.joint_points)
