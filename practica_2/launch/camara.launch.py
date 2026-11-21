"""
Camara.launch.py

Arranca el publicador de imágenes de usb_cam y el visor rqt_image_view
para mostrar las imágenes de la cámara.
"""

from launch import LaunchDescription
from launch_ros.actions import Node

ESPACIO_NOMBRES_CAMARA: str = "usb_cam"
TOPIC_IMAGEN: str = f"/{ESPACIO_NOMBRES_CAMARA}/image_raw"


def generate_launch_description() -> LaunchDescription:
    """Describe los nodos que se lanzan: el publicador de la cámara y el visor.

    Returns:
        Descripción del lanzamiento con los dos nodos.
    """
    return LaunchDescription(
        [
            # Publicador: lee la cámara y publica cada fotograma como sensor_msgs/Image
            Node(
                package="usb_cam",
                executable="usb_cam_node_exe",
                name="usb_cam",
                namespace=ESPACIO_NOMBRES_CAMARA,
                output="screen",
            ),
            # Visor: se suscribe al topic de la cámara y muestra las imágenes en una ventana
            Node(
                package="rqt_image_view",
                executable="rqt_image_view",
                name="visor_imagenes",
                arguments=[TOPIC_IMAGEN],
                output="screen",
            ),
        ]
    )