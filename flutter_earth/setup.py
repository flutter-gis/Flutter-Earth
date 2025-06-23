"""Setup script for Flutter Earth."""
from setuptools import setup, find_packages

setup(
    name="flutter-earth",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "rasterio>=1.2.0",
        "pyshp>=2.1.0",
        "folium>=0.12.0",
        "pywebview>=3.6.0",
        "requests>=2.26.0",
        "python-dateutil>=2.8.2",
        "PyQt6>=6.4.0",
        "PyQt6-WebEngine>=6.4.0",
        "earthengine-api>=0.1.290",
        "google-api-python-client>=2.0.0",
        "google-auth>=2.0.0",
        "google-auth-httplib2>=0.1.0"
    ],
    entry_points={
        'console_scripts': [
            'flutter-earth=main:main',
        ],
    },
    author="Flutter Earth Project",
    description="A modern tool for downloading and processing satellite imagery from Google Earth Engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    keywords=["earth-engine", "satellite", "imagery", "gis", "remote-sensing"],
    url="https://github.com/flutter-earth/flutter-earth",
    project_urls={
        "Bug Tracker": "https://github.com/flutter-earth/flutter-earth/issues",
        "Documentation": "https://flutter-earth.readthedocs.io",
    },
) 