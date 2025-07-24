from setuptools import setup, find_packages

setup(
    name='drone-sdk',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A comprehensive SDK for drone telemetry, sensors, and extensions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/drone-sdk',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'opencv-python',
        'flask',
        'filterpy',
        'tensorflow',  # Optional, if using AIMLIntegration
        'torch',       # Optional, if using AIMLIntegration
        'pyserial',    # For LIDAR sensor communication
        'RPi.GPIO'     # For Raspberry Pi GPIO control
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)