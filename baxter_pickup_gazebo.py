#!/usr/bin/env python
import rospy
from baxter_pickup_msgs.msg import BlockArray
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Quaternion,
)
from std_msgs.msg import (
    String,
    Header,
    Empty,
)
import baxter_interface
from baxter_pickup_msgs.srv import BaxterIK, BaxterIKRequest
import copy
class BaxterPickup:
    def __init__(self, limb, name, ID):
        # Initialize Node
        rospy.init_node('grabber', anonymous=True)
        # Subscribe to sensor data
        rospy.Subscriber("/block_location", BlockArray, self.model_callback)
        # Contains a list of block locations for blocks visible by Baxter
        self._name = name
        self._ID = ID
        self._block_locations = []
        self._check_for_blocks = False
        # Select limb (left or right)
        self._limb = baxter_interface.Limb(limb)
        # Set movement speed
        self._limb.set_joint_position_speed(0.05)
        # Initialize Gripper
        self._gripper = baxter_interface.Gripper(limb)
        # Initialize inverse kinematics service
        self._ik = rospy.ServiceProxy('/Baxter_IK_left/', BaxterIK)
        print("Getting robot state... ")
        self._rs = baxter_interface.RobotEnable(baxter_interface.CHECK_VERSION)
        self._init_state = self._rs.state().enabled
        print("Enabling robot... ")
        self._rs.enable()
        # An orientation for gripper fingers to be overhead and parallel to an object - use these values for orientation when you query the IK service
        self._overhead_orientation = Quaternion(
                             x=-0.0249590815779,
                             y=0.999649402929,
                             z=0.00737916180073,
                             w=0.00486450832011)
        # Start position - use these angles for the robot's start position
        self._start_position = {'left_w0': 0.6699952259595108,
                             'left_w1': 1.030009435085784,
                             'left_w2': -0.4999997247485215,
                             'left_e0': -1.189968899785275,
                             'left_e1': 1.9400238130755056,
                             'left_s0': -0.08000397926829805,
                             'left_s1': -0.9999781166910306}
        # Position over the trash can - use these angles for the robot's position over the trash can
        self._trashcan_position = {'left_w0': 0.3699952259595108,
                             'left_w1': 1.030009435085784,
                             'left_w2': -0.999997247485215,
                             'left_e0': -1.189968899785275,
                             'left_e1': 1.9400238130755056,
                             'left_s0': 1.78000397926829805,
                             'left_s1': -0.9999781166910306}
    def move_to_start(self):
        self._limb.move_to_joint_positions(self._start_position)

    def move_to_approach_position(self, point):
        pp = point
        pp.y += 0.15
        print pp.x
        print pp.y
        print pp.z

    # def move_to_pickup_position(self, point):
    #     # Implement this function - Baxter's limb should be at the target block with it's gripper open but around the target block

    # def grip(self):
    #     # Implement this function - close Baxter's gripper

    # def ungrip(self):
    #     # Implement this function - open Baxter's gripper

    def move_to_trashcan(self):
        self._limb.move_to_joint_positions(self._trashcan_position)

    def model_callback(self,data): 
        # If looking for blocks, copy locations of found blocks to _block_locations   
        if self._check_for_blocks==True:
            self._block_locations=data
	    self._check_for_blocks=False
    def main(self):
        # Program loop goes here
        while(True):
            self._check_for_blocks=True
            if self._block_locations:
                if len(self._block_locations.block_poses)==0:
                    print "Finished"
                    finished_str = self._ID + ":" + self._name
                    pub_finished = rospy.Publisher('/pickup_finished', String, queue_size=100)
                    rospy.sleep(1) 
                    pub_finished.publish(finished_str)
                    rospy.sleep(0.5)
                    return
               	self.move_to_start()
                for x in self._block_locations.block_poses:
                    self.move_to_approach_position(x.point)
                return
        
if __name__ == "__main__":
    student_name = raw_input("Enter the your name (Last, First): ")
    student_ID = raw_input("Enter the UID: ")
    bp = BaxterPickup("left", student_name, student_ID)
    bp.main()
    


