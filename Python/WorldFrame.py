from math import sqrt, atan2, cos, sin

#from math import abs

class WorldFrame:
    def __init__(self, cam1_mark_dist, cam2_mark_dist, cam1_cam2_dist, 
                 mark_screen_coord_side, mark_screen_coord_ventral, 
                 focal_length_side, focal_length_ventral, 
                 screen_resolution_side, screen_resolution_ventral):
        
        ## Save the parameters in the WorldFrameData object
        self.d1 = cam1_mark_dist
        self.D2 = cam2_mark_dist
        self.Th = cam1_cam2_dist

        self.x1_M_s = mark_screen_coord_side[0]
        self.y1_M_s = mark_screen_coord_side[1]
        self.x2_M_s = mark_screen_coord_ventral[0]
        self.y2_M_s = mark_screen_coord_ventral[1]

        self.f1 = focal_length_side
        self.f2 = focal_length_ventral

        self.W1 = screen_resolution_side[0]
        self.H1 = screen_resolution_side[1]
        self.W2 = screen_resolution_ventral[0]
        self.H2 = screen_resolution_ventral[1]

        ## Use of the calculated formulas to determine the parameters needed to change frame
        self.delta_y_1 = -(self.d1 / self.f1) * (self.y1_M_s - self.H1/2)
        self.delta_x_2 = -(self.D2 / self.f2) * (self.x2_M_s - self.W2/2)
        self.delta_z_2 = (self.D2 / self.f2) * (self.y2_M_s - self.H2/2)

        self.h1 = self.Th - self.D2 - self.delta_y_1
        self.l1 = sqrt(self.h1**2 + self.d1**2)

        self.delta_x_1 = -(self.l1 / self.f1) * (self.x1_M_s - self.W1/2)

        self.theta1 = atan2(self.h1, self.d1)

    def to_3D(self, screen_coord_1, screen_coord_2):
        # Get the screen coordinates
        x1_s = screen_coord_1[0]
        y1_s = screen_coord_1[1]
        x2_s = screen_coord_2[0]
        y2_s = screen_coord_2[1]

        # Define the temporary variables
        ap = (cos(self.theta1)/self.f1) * (y1_s - self.H1/2) - sin(self.theta1)
        b = self.l1 * sin(self.theta1) + self.delta_y_1 + self.D2
        cp = (sin(self.theta1)/self.f1) * (y1_s - self.H1/2) + cos(self.theta1)
        d = self.l1 * cos(self.theta1) + self.delta_z_2
        ep = -(y2_s - self.H2/2)/self.f2

        # Calculate the distances to the cameras along their z_c axis
        z1_c = (d - ep*b)/(ep*ap - cp)
        z2_c = (cp*b - ap*d)/(cp - ap*ep)

        # Calculate the world frame coordinates of the point
        x_w = (z1_c/self.f1) * (x1_s - self.W1/2) + self.delta_x_1
        #x_w = (z2_c/self.f2) * (x2_s - self.W2/2) + self.delta_x_2
        y_w = z2_c - self.D2
        z_w = -(z2_c/self.f2) * (y2_s - self.H2/2) + self.delta_z_2

        # Show the difference between the 2 ways of getting the position
        print("x diff :", abs(x_w - ((z2_c/self.f2) * (x2_s - self.W2/2) + self.delta_x_2)))
        print("y diff :", abs(y_w - ((z1_c/self.f1) * (y1_s - self.H1/2) * cos(self.theta1) - (z1_c-self.l1) * sin(self.theta1) + self.delta_y_1)))
        print("z diff :", abs(z_w - ((z1_c/self.f1) * (y1_s - self.H1/2) * sin(self.theta1) + (z1_c-self.l1) * cos(self.theta1))))

        return (x_w, y_w, z_w)
