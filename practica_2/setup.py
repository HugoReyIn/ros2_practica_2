"""
Setup.py

Instalación del paquete ROS 2 ros2_practica_2.
"""
from glob import glob
from setuptools import find_packages, setup

package_name = 'practica_2'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ignacio',
    maintainer_email='ignacio@todo.todo',
    description='Ingesta, calibración y procesamiento de imágenes con ROS 2. Práctica 2',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'recolector_imagenes = ros2_practica_2.recolector_imagenes:main',
            'aplicador_calibracion = practica_2.aplicador_calibracion:main',
        ],
    },
)