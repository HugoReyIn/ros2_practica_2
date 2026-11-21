"""
RecolectorImagenes.py

Se suscribe al topic de la cámara, ingiere 10 imágenes seguidas
distintas entre sí y las guarda en disco.
"""

from typing import Optional

import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image

from practica_2.detector_cambios import DetectorCambios
from practica_2.guardado_imagenes import GuardadorImagenes

# Configuración del nodo
NODO: str = "recolector_imagenes"
TOPIC_IMAGEN: str = "/usb_cam/image_raw"

# Capacidad de la cola de suscripción
TAMANO_COLA: int = 10

# Número de imágenes distintas que hay que capturar
NUMERO_IMAGENES: int = 10

# Tiempo mínimo entre dos capturas, en segundos.
INTERVALO_MINIMO_SEGUNDOS: float = 1.0

# Codificación de la imagen de OpenCV: BGR de 8 bits
CODIFICACION_OPENCV: str = "bgr8"

# Conversión de nanosegundos a segundos
NANOSEGUNDOS_AL_SEGUNDO: float = 1e9


class RecolectorImagenes(Node):
    """Nodo que guarda las primeras NUMERO_IMAGENES imágenes distintas que recibe."""

    def __init__(self, numero_imagenes: int = NUMERO_IMAGENES) -> None:
        """Inicializa los componentes y la suscripción al topic de la cámara.

        Args:
            numero_imagenes: Cantidad de imágenes distintas que se capturan.
        """
        super().__init__(NODO)
        self._numero_imagenes = numero_imagenes
        self._puente = CvBridge()
        self._detector = DetectorCambios()
        self._guardador = GuardadorImagenes()
        self._imagenes_guardadas: int = 0
        # Se guarda preprocesada para no repetir el preprocesado en cada comparación
        self._ultima_preprocesada: Optional[np.ndarray] = None
        self._tiempo_ultima_captura: Optional[float] = None

        self.create_subscription(Image, TOPIC_IMAGEN, self._imagen_recibida, TAMANO_COLA)
        self.get_logger().info(f"Escuchando {TOPIC_IMAGEN}")

    @property
    def completado(self) -> bool:
        """Indica si ya se han guardado todas las imágenes."""
        return self._imagenes_guardadas >= self._numero_imagenes

    def _imagen_recibida(self, mensaje: Image) -> None:
        """Procesa un mensaje recibido de la cámara y lo guarda si es distinto.

        Args:
            mensaje: Imagen publicada por usb_cam.
        """
        # Pueden llegar mensajes que ya estaban en la cola después de terminar
        if self.completado:
            return

        tiempo = self._tiempo_a_segundos(mensaje)
        if not self._ha_pasado_intervalo(tiempo):
            return

        imagen = self._puente.imgmsg_to_cv2(mensaje, desired_encoding=CODIFICACION_OPENCV)
        preprocesada = self._detector.preprocesar(imagen)
        # La primera imagen siempre se guarda: no hay ninguna con la que compararla
        if (self._ultima_preprocesada is not None
                and not self._detector.es_distinta(self._ultima_preprocesada, preprocesada)):
            return

        ruta = self._guardador.guardar(self._imagenes_guardadas, imagen)
        self._imagenes_guardadas += 1
        self._ultima_preprocesada = preprocesada
        self._tiempo_ultima_captura = tiempo
        self.get_logger().info(
            f"Imagen {self._imagenes_guardadas}/{self._numero_imagenes} guardada en {ruta}")

    def _ha_pasado_intervalo(self, tiempo: float) -> bool:
        """Comprueba si ha pasado el intervalo mínimo desde la última captura.

        Args:
            tiempo: Tiempo de la imagen recibida, en segundos.

        Returns:
            True si se puede capturar o
            False si la última captura es demasiado reciente.
        """
        if self._tiempo_ultima_captura is None:
            return True
        return tiempo - self._tiempo_ultima_captura >= INTERVALO_MINIMO_SEGUNDOS

    @staticmethod
    def _tiempo_a_segundos(mensaje: Image) -> float:
        """Junta el tiempo de segundos y nanosegundos y los convierte en segundos.

        Se usa la marca de tiempo de la cabecera, que indica cuándo se capturó
        el fotograma, y no cuándo llegó al nodo.

        Args:
            mensaje: Imagen recibida.

        Returns:
            Tiempo en segundos.
        """
        tiempo = mensaje.header.stamp
        return tiempo.sec + tiempo.nanosec / NANOSEGUNDOS_AL_SEGUNDO


def main() -> None:
    """Inicializa ROS 2, ejecuta el nodo hasta guardar todas las imágenes y lo cierra."""
    rclpy.init()
    nodo = RecolectorImagenes()
    try:
        # spin_once en lugar de spin para poder salir al completar la captura
        while rclpy.ok() and not nodo.completado:
            rclpy.spin_once(nodo)
        nodo.get_logger().info("Captura completada")
    except (KeyboardInterrupt, ExternalShutdownException):
        pass  # Cierre normal con Ctrl+C
    finally:
        nodo.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()