from Camera import CameraData

from math import sqrt, atan2, cos, sin


#from math import abs

class WorldFrame:
    def __init__(self, cam1_mark_dist:float, cam2_mark_dist:float, cam1_cam2_dist:float, 
                 mark_screen_coord_side:tuple[int, int], mark_screen_coord_ventral:tuple[int, int], 
                 camera_side:CameraData, camera_ventral:CameraData):
        
        ## Save the parameters in the WorldFrameData object
        self.camera_side = camera_side
        self.camera_ventral = camera_ventral

        self.d1 = cam1_mark_dist
        self.D2 = cam2_mark_dist
        self.Th = cam1_cam2_dist

        self.x1_M_s = camera_side.px_to_meter(mark_screen_coord_side[0])
        self.y1_M_s = camera_side.px_to_meter(mark_screen_coord_side[1])
        self.x2_M_s = camera_ventral.px_to_meter(mark_screen_coord_ventral[0])
        self.y2_M_s = camera_ventral.px_to_meter(mark_screen_coord_ventral[1])

        self.f1 = camera_side.focal_length
        self.f2 = camera_ventral.focal_length

        self.W1_px = camera_side.resolution[0]
        self.H1_px = camera_side.resolution[1]
        self.W2_px = camera_ventral.resolution[0]
        self.H2_px = camera_ventral.resolution[1]

        self.W1 = self.camera_side.px_to_meter(self.W1_px)
        self.H1 = self.camera_side.px_to_meter(self.H1_px)
        self.W2 = self.camera_ventral.px_to_meter(self.W2_px)
        self.H2 = self.camera_ventral.px_to_meter(self.W2)

        ## Use of the calculated formulas to determine the parameters needed to change frame
        self.x1_M_s_t, self.y1_M_s_t = self.to_center_screen_coord((self.x1_M_s, self.y1_M_s), (self.H1, self.W1))
        self.x2_M_s_t, self.y2_M_s_t = self.to_center_screen_coord((self.x2_M_s, self.y2_M_s), (self.H2, self.W2))

        self.delta_y_1 = -(self.d1 / self.f1) * self.y1_M_s_t
        self.delta_x_2 = -(self.D2 / self.f2) * self.x2_M_s_t
        self.delta_z_2 = (self.D2 / self.f2) * self.y2_M_s_t

        self.h1 = self.Th - self.D2 - self.delta_y_1
        self.l1 = sqrt(self.h1**2 + self.d1**2)

        self.delta_x_1 = -(self.l1 / self.f1) * self.x1_M_s_t

        # Theta1 in radian
        self.theta1 = atan2(self.h1, self.d1)

        print("theta1 :", self.theta1)
        print("y1_M_s :", self.y1_M_s, "- y2_M_s :", self.y2_M_s)
        print("x1_M_s :", self.x1_M_s, "- x2_M_s :", self.x2_M_s)
        print("f1 :", self.f1, "- f2 :", self.f2)
        print("Th :", self.Th, "- D2 :", self.D2)
        print("d1 :", self.d1, "- h1 :", self.h1)
        print("delta_z_2 :", self.delta_z_2, "- delta_y_1 :", self.delta_y_1)
        print("delta_x_1 :", self.delta_x_1, "- delta_x_2 :", self.delta_x_2)
        print("H1 :", self.H1, "- H2 :", self.H2)
        print("W1 :", self.W1, "- W2 :", self.W2)

    def to_center_screen_coord(self, coord_px:int, screen_length_px:int, value_origin_upper_left:bool=True):
        if value_origin_upper_left:
            return (screen_length_px[0]/2 - coord_px[0], screen_length_px[1]/2 - coord_px[1])
        else:
            return (coord_px[0] - screen_length_px[0]/2, coord_px[1] - screen_length_px[1]/2)

    def to_3D(self, screen_coord_side:tuple[int, int], screen_coord_ventral:tuple[int, int]):
        # Get the screen coordinates
        x1_s = self.camera_side.px_to_meter(screen_coord_side[0])
        y1_s = self.camera_side.px_to_meter(screen_coord_side[1])
        x2_s = self.camera_ventral.px_to_meter(screen_coord_ventral[0])
        y2_s = self.camera_ventral.px_to_meter(screen_coord_ventral[1])

        # Convert to frame on the center of the window
        x1_s_t, y1_s_t = self.to_center_screen_coord(coord_px=(x1_s, y1_s), screen_length_px=(self.H1, self.W1))
        x2_s_t, y2_s_t = self.to_center_screen_coord(coord_px=(x2_s, y2_s), screen_length_px=(self.H2, self.W2))

        # Define the temporary variables
        ap = (cos(self.theta1)/self.f1) * y1_s_t - sin(self.theta1)
        b = self.l1 * sin(self.theta1) + self.delta_y_1 + self.D2
        cp = (sin(self.theta1)/self.f1) * y1_s_t + cos(self.theta1)
        d = -(self.l1 * cos(self.theta1) + self.delta_z_2)
        ep = -y2_s_t/self.f2

        # Calculate the distances to the cameras along their z_c axis
        z1_c = (d - ep*b)/(ep*ap - cp)
        z2_c = (cp*b - ap*d)/(cp - ap*ep)

        #print("z1_c :", z1_c, "- z2_c :", z2_c)

        # Calculate the world frame coordinates of the point
        x_w = (z1_c/self.f1) * x1_s_t + self.delta_x_1
        #x_w = (z2_c/self.f2) * (x2_s - self.W2/2) + self.delta_x_2
        y_w = z2_c - self.D2
        z_w = -(z2_c/self.f2) * y2_s_t + self.delta_z_2

        # Show the difference between the 2 ways of getting the position
        # print("x diff :", abs(x_w - ((z2_c/self.f2) * x2_s_t + self.delta_x_2)))
        # #print("x diff :", abs(x_w - ((z1_c/self.f1) * x1_s_t + self.delta_x_1)))
        # print("y diff :", abs(y_w - ((z1_c/self.f1) * y1_s_t * cos(self.theta1) - (z1_c-self.l1) * sin(self.theta1) + self.delta_y_1)))
        # print("z diff :", abs(z_w - ((z1_c/self.f1) * y1_s_t * sin(self.theta1) + (z1_c-self.l1) * cos(self.theta1))))

        return (x_w, y_w, z_w)
