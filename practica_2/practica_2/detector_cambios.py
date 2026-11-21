"""
DetectorCambios.py

Decide si una imagen es suficientemente distinta de la última guardada.
"""

from typing import Tuple

import cv2
import numpy as np

# Diferencia de intensidad (0-255) a partir de la cual un píxel se considera cambiado.
# Por debajo, la diferencia se atribuye al ruido del sensor.
UMBRAL_DIFERENCIA_PIXEL: int = 25

# Fracción mínima de píxeles cambiados para considerar que la imagen es distinta
PROPORCION_MINIMA_CAMBIO: float = 0.05

# Tamaño del núcleo del desenfoque gaussiano.
TAMANO_NUCLEO_DESENFOQUE: Tuple[int, int] = (21, 21)

# Con desviación 0, OpenCV la calcula a partir del tamaño del núcleo
DESVIACION_DESENFOQUE: int = 0

# Valor que toman en la máscara binaria los píxeles que superan el umbral
VALOR_MASCARA: int = 255


class DetectorCambios:
    """Compara dos imágenes y decide si la escena ha cambiado entre ellas."""

    def __init__(self, umbral_diferencia_pixel: int = UMBRAL_DIFERENCIA_PIXEL,
                 proporcion_minima_cambio: float = PROPORCION_MINIMA_CAMBIO) -> None:
        """Inicia el detector con sus umbrales.

        Args:
            umbral_diferencia_pixel: Diferencia de intensidad (0-255) para considerar
                que un píxel ha cambiado.
            proporcion_minima_cambio: Fracción de píxeles cambiados (0-1) a partir de
                la cual las imágenes se consideran distintas.
        """
        self.umbral_diferencia_pixel = umbral_diferencia_pixel
        self.proporcion_minima_cambio = proporcion_minima_cambio

    @staticmethod
    def preprocesar(imagen: np.ndarray) -> np.ndarray:
        """Pasa la imagen a escala de grises y la desenfoca.

        El color no aporta información para detectar cambios y el desenfoque
        (filtro paso bajo) evita que el ruido de la cámara se detecte como cambio.

        Args:
            imagen: Imagen BGR de OpenCV.

        Returns:
            Imagen en escala de grises desenfocada.
        """
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gris, TAMANO_NUCLEO_DESENFOQUE, DESVIACION_DESENFOQUE)

    def es_distinta(self, anterior_preprocesada: np.ndarray,
                    actual_preprocesada: np.ndarray) -> bool:
        """Comprueba si la proporción de píxeles cambiados supera el umbral.

        Se umbraliza cada píxel en lugar de usar la diferencia media para que un
        cambio leve de iluminación en toda la imagen no cuente como imagen distinta.

        Args:
            anterior_preprocesada: Última imagen guardada, ya preprocesada.
            actual_preprocesada: Imagen recibida, ya preprocesada.

        Returns:
            True si las imágenes son distintas o
            False en caso contrario.
        """
        diferencia = cv2.absdiff(anterior_preprocesada, actual_preprocesada)
        _, mascara = cv2.threshold(diferencia, self.umbral_diferencia_pixel,
                                   VALOR_MASCARA, cv2.THRESH_BINARY)
        proporcion_cambiada = cv2.countNonZero(mascara) / mascara.size
        return proporcion_cambiada > self.proporcion_minima_cambio