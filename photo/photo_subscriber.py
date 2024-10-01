import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge,CvBridgeError
from photo import distribute_photo

class ImageClickPublisher(Node):
    def __init__(self):
        super().__init__('situation_image')
        # publisher
        self.image_pubs = [
            self.create_publisher(Image, 'environment_image', 1),
            self.create_publisher(Image, 'debris_image', 1),
            self.create_publisher(Image, 'victim_image', 1)
        ]
        self.txt_publisher = self.create_publisher(String, 'photo_result',1)
        self.bridge = CvBridge()
       
        self.topic_sub = self.create_subscription(
            Image,
            'input_photo_image',
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        try:
            cv_bridge = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            texts = ["Environment","Debris","Victim"]
            num = distribute_photo.distribute(cv_bridge,texts)

            text = distribute_photo.write_param()
            
            photo_result_txt = String()
            photo_result_txt.data = text
            self.txt_publisher.publish(photo_result_txt)
            result_image = self.bridge.cv2_to_imgmsg(cv_bridge,'bgr8')
            self.image_pubs[num].publish(result_image)
        except CvBridgeError as e:
            self.get_logger().error(f'Failed to convert image: {e}')



def main(args=None):
    rclpy.init(args=args)
    node = ImageClickPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
