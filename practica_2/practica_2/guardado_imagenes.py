"""
GuardadoImagenes.py

Guarda en disco las imágenes capturadas.
"""

from pathlib import Path

import cv2
import numpy as np

# Carpeta de las imágenes, relativa al directorio desde el que se lanza el nodo
CARPETA_IMAGENES: Path = Path("imagenes")
PREFIJO_IMAGEN: str = "imagen_"
EXTENSION_IMAGEN: str = ".png"

# Dígitos del número de imagen, para que se ordenen bien
DIGITOS_INDICE: int = 2


class GuardadorImagenes:
    """Escribe las imágenes en una carpeta con un nombre numerado."""

    def __init__(self, carpeta: Path = CARPETA_IMAGENES) -> None:
        """Crea la carpeta de destino si no existe.

        Args:
            carpeta: Ruta donde se guardan las imágenes.
        """
        self._carpeta = carpeta
        self._carpeta.mkdir(parents=True, exist_ok=True)

    def guardar(self, indice: int, imagen: np.ndarray) -> Path:
        """Guarda una imagen como `<carpeta>/imagen_<indice>.png`.

        Si el fichero ya existe, se sobrescribe.

        Args:
            indice: Número de la imagen dentro de la captura.
            imagen: Imagen BGR de OpenCV.

        Returns:
            Ruta del fichero escrito.

        Raises:
            OSError: Si OpenCV no puede escribir el fichero.
        """
        ruta = self._carpeta / f"{PREFIJO_IMAGEN}{indice:0{DIGITOS_INDICE}d}{EXTENSION_IMAGEN}"
        if not cv2.imwrite(str(ruta), imagen):
            raise OSError(f"No se pudo guardar la imagen en {ruta}")
        return ruta