#!/usr/bin/env python3

# Copyright 2020 Spirit AeroSystems

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Author: Bharath Rao
#


import os
import sys
import cv2
from cv_bridge import CvBridge

import rospy
from sensor_msgs.msg import Image

__NODE_FREQUENCY__ = 1  # Hz


class ImagePublisher(object):

    # -----------------
    def __init__(self):

        rospy.loginfo('[%s] Node initiated ...', rospy.get_name())

        self.bridge = CvBridge()
        self.publisher_ = rospy.Publisher('/image', Image, latch=False, queue_size=1)
        self.image_files: list = self.get_absolute_file_paths('~/Pictures/')
        #
        self.index = 0
        self.max_index = len(self.image_files) - 1

    # -----------------
    def publish(self):
        # rospy.loginfo('Publishing: %s', self.image_files[self.index])
        # read rgb image file
        cv_image = cv2.imread(self.image_files[self.index], cv2.IMREAD_COLOR)
        # self.publisher_.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))

        # add alpha channel (not working; underlying api does not support) ¯\_(ツ)_/¯
        cv_image_rgba = cv2.cvtColor(cv_image, cv2.COLOR_RGB2RGBA)
        sh = cv_image_rgba.shape
        for i in range(0, sh[0]):
            for j in range(0, sh[1]):
                cv_image_rgba[i, j, 3] = 255
        #
        self.publisher_.publish(self.bridge.cv2_to_imgmsg(cv_image_rgba, "bgra8"))
        #
        if self.index < self.max_index:
            self.index += 1
        else:
            self.index = 0

    # -----------------
    def get_absolute_file_paths(self, directory):
        path_list = []
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                if 'jpg' in f or 'png' in f:
                    path_list.append(os.path.abspath(os.path.join(dirpath, f)))
        return path_list


if __name__ == '__main__':
    # Strip the command line to remove any ROS run-time inserted arguments
    __argv = rospy.myargv(argv=sys.argv)
    # Set defaults
    __node_name__ = 'image_publisher'
    # # Check if a command line argument has been passed

    try:
        rospy.init_node(__node_name__)
        RATE = rospy.Rate(__NODE_FREQUENCY__)  # 1 hz

        NOM_FAST_DISP = ImagePublisher()

        # Either use the while loop
        while not rospy.is_shutdown():
            NOM_FAST_DISP.publish()
            RATE.sleep()

        # Or use the spin - but not both
        # rospy.spin()

    except rospy.ROSInterruptException:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
