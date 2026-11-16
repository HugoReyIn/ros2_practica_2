# Práctica 2 — Ingesta, calibración y procesamiento de imágenes con ROS 2

Paquete de ROS 2 Jazzy para recibir imágenes de una cámara con `usb_cam`, calibrarla con `camera_calibration` y aplicar la calibración con OpenCV usando `cv_bridge`.

**Autores:** Hugo · Xabier

---

## Requisitos

- Entorno Docker de la asignatura (ROS 2 Jazzy + VS Code)
- Paquetes de ROS 2: `usb_cam`, `camera_calibration`, `cv_bridge`
- OpenCV (`python3-opencv`)
- Tablero de ajedrez para la calibración

Para arrancar el entorno:

```bash
./lab.sh iniciar        # Linux
lab.bat iniciar         # Windows
```

---

## Reparto de tareas

### Parte 1: Requisitos

| Responsable | Tarea | Subtareas | Estado |
|---|---|---|---|
| **Hugo** | **1. Publicador de imágenes** | Crear el paquete (`package.xml`, `setup.py`, entry points) · parámetros de `usb_cam` en `config/` · launch file · comprobar con `rqt_graph` y `ros2 topic hz` | [ ] |
| **Hugo** | **2. Suscriptor e ingesta** | Nodo `ImageCollector` · suscriptor al topic de imagen · filtro para que las 10 imágenes sean distintas (diferencia entre fotogramas / MSE con umbral) · guardado en disco | `[ ] |
| **Xabier** | **3. Calibración** | Calibrar con `cameracalibrator` y el tablero · guardar el `.yaml` en `config/` · documentar el procedimiento | [ ] |
| **Xabier** | **4. Aplicar la calibración** | Nodo `CalibrationApplier` · cargar los parámetros del `.yaml` · convertir `Image` → OpenCV con `cv_bridge` · aplicar `cv2.undistort` y publicar o mostrar la imagen corregida | [ ] |

**Orden recomendado:** Hugo hace primero la tarea 1, porque bloquea al resto. Mientras tanto, Xabier puede calibrar lanzando `usb_cam` a mano (`ros2 run usb_cam usb_cam_node_exe`). Después cada uno sigue con su tarea difícil en paralelo.

---

## Estructura prevista

```
<nombre_paquete>/
├── <nombre_paquete>/
│   ├── __init__.py
│   ├── image_collector.py        # Tarea 2 (Hugo)
│   └── calibration_applier.py    # Tarea 4 (Xabier)
├── launch/
│   ├── camera.launch.py          # Tarea 1 (Hugo)
│   └── full_pipeline.launch.py   # Cierre (Xabier)
├── config/
│   ├── usb_cam_params.yaml       # Xabier
│   └── camera_calibration.yaml   # Tarea 3 (Xabier)
├── images/                       # Salida de la tarea 2
├── package.xml
├── setup.py
└── README.md
```

---

## Uso

```bash
# Compilar
colcon build --packages-select <nombre_paquete>
source install/setup.bash

# 1. Publicar imágenes de la cámara
ros2 launch <nombre_paquete> camera.launch.py

# 2. Capturar 10 imágenes distintas
ros2 run <nombre_paquete> image_collector

# 3. Calibrar (ajustar --size y --square al tablero real)
ros2 run camera_calibration cameracalibrator \
  --size 8x6 --square 0.025 \
  --ros-args -r image:=/image_raw -p camera:=/camera

# 4. Aplicar la calibración
ros2 run <nombre_paquete> calibration_applier
```

---

## Normas de código

- Programación orientada a objetos, código limpio y bien estructurado
- Docstrings en todas las clases y funciones, y comentarios que expliquen el porqué (no los triviales)
- Type hints en parámetros, retornos y atributos
- PEP-8:
  - `variables_y_funciones` en minúsculas con barra baja
  - `NombresDeClases` en PascalCase
  - `_metodos_privados` con barra baja delante
  - Sin números mágicos: umbrales, rutas y números de imágenes como constantes con nombre

---

## Flujo de trabajo con Git

> La nota es individual y se calcula **solo a partir de los commits** de cada uno.

1. **Identidad:** cada uno configura `git config user.name` y `git config user.email` con el email de su cuenta de GitHub.
2. **Ramas:** una por tarea (`feature/image-collector`, `feature/calibration`, `feature/calibration-applier`…).
3. **Integración:** Pull Request a `main`; cada uno sube su propio trabajo.
4. **Commits pequeños y descriptivos**, por ejemplo:
   - `feat: esqueleto del nodo ImageCollector`
   - `feat: filtro de imágenes duplicadas por MSE`
   - `docs: docstrings y type hints en ImageCollector`
5. **Fecha límite:** ningún commit después del plazo, ni siquiera para arreglar el README. Si no, cuenta como entrega tardía.

---

## Entrega

Solo la URL del repositorio de GitHub. Hay que comprobar que el equipo docente puede acceder y que no hay contribuidores externos al grupo.
