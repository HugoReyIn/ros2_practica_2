"""
AplicadorCalibracion.py

Se suscribe al topic de la cámara, corrige la distorsión de cada imagen
con los parámetros obtenidos con camera_calibration y publica el resultado.
"""

from typing import Tuple

import cv2
import numpy as np
import rclpy
import yaml
from cv_bridge import CvBridge
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image

# Configuración del nodo
NODO: str = "aplicador_calibracion"
TOPIC_IMAGEN: str = "/usb_cam/image_raw"
TOPIC_CORREGIDA: str = "/usb_cam/image_corregida"

# Capacidad de la cola de suscripción y publicación
TAMANO_COLA: int = 10

# Codificación de la imagen de OpenCV: BGR de 8 bits
CODIFICACION_OPENCV: str = "bgr8"

# Fichero generado por camera_calibration, relativo al directorio desde el que se lanza el nodo
RUTA_CALIBRACION: str = "config/calibracion_camara.yaml"

# Claves del yaml que genera camera_calibration
CLAVE_MATRIZ_CAMARA: str = "camera_matrix"
CLAVE_COEFICIENTES_DISTORSION: str = "distortion_coefficients"
CLAVE_DATOS: str = "data"
CLAVE_FILAS: str = "rows"
CLAVE_COLUMNAS: str = "cols"

class AplicadorCalibracion(Node):
    """Nodo que publica las imágenes de la cámara sin distorsión."""
    def __init__(self, ruta_calibracion: str = RUTA_CALIBRACION) -> None:
        """Carga la calibración y crea el suscriptor y el publicador.

        Args:
            ruta_calibracion: Ruta del yaml generado por camera_calibration.
        """
        super().__init__(NODO)
        self._puente = CvBridge()
        self._matriz_camara, self._coeficientes_distorsion = self._cargar_calibracion(
            ruta_calibracion)

        self.create_subscription(Image, TOPIC_IMAGEN, self._imagen_recibida, TAMANO_COLA)
        self._publicador = self.create_publisher(Image, TOPIC_CORREGIDA, TAMANO_COLA)
        self.get_logger().info(f"Corrigiendo {TOPIC_IMAGEN} y publicando en {TOPIC_CORREGIDA}")

    @staticmethod
    def _cargar_calibracion(ruta: str) -> Tuple[np.ndarray, np.ndarray]:
        """Lee la matriz de la cámara y los coeficientes de distorsión del yaml.

        Args:
            ruta: Ruta del yaml generado por camera_calibration.

        Returns:
            Matriz de la cámara (3x3) y coeficientes de distorsión.
        """
        with open(ruta, "r", encoding="utf-8") as fichero:
            datos = yaml.safe_load(fichero)

        # El yaml guarda cada matriz como una lista plana más sus dimensiones,
        # así que se reconstruye con reshape usando las filas y columnas indicadas
        matriz = datos[CLAVE_MATRIZ_CAMARA]
        matriz_camara = np.array(matriz[CLAVE_DATOS]).reshape(
            matriz[CLAVE_FILAS], matriz[CLAVE_COLUMNAS])
        coeficientes_distorsion = np.array(datos[CLAVE_COEFICIENTES_DISTORSION][CLAVE_DATOS])
        return matriz_camara, coeficientes_distorsion

    def _imagen_recibida(self, mensaje: Image) -> None:
        """Corrige la distorsión de la imagen recibida y la publica.

        Args:
            mensaje: Imagen publicada por usb_cam.
        """
        imagen = self._puente.imgmsg_to_cv2(mensaje, desired_encoding=CODIFICACION_OPENCV)
        corregida = cv2.undistort(imagen, self._matriz_camara, self._coeficientes_distorsion)

        salida = self._puente.cv2_to_imgmsg(corregida, encoding=CODIFICACION_OPENCV)
        # Se conserva la cabecera original para mantener la marca de tiempo de la captura
        salida.header = mensaje.header
        self._publicador.publish(salida)


def main() -> None:
    """Inicializa ROS 2, ejecuta el nodo hasta que se interrumpe y lo cierra."""
    rclpy.init()
    nodo = AplicadorCalibracion()
    try:
        rclpy.spin(nodo)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass  # Cierre normal con Ctrl+C
    finally:
        nodo.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()