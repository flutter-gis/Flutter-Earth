"""Setup script for Flutter Earth."""
from setuptools import setup, find_packages

setup(
    name="flutter_earth",
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
        "PyQt5>=5.15.0",
        "PyQtWebEngine>=5.15.0",
        "earthengine-api>=0.1.290",
        "google-api-python-client>=2.0.0",
        "google-auth>=2.0.0",
        "google-auth-httplib2>=0.1.0"
    ],
    entry_points={
        'console_scripts': [
            'flutter-earth=flutter_earth.flutter_earth_6_19:main',
        ],
    },
    author="Flutter Earth Project",
    description="A tool for downloading and processing satellite imagery from Google Earth Engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
) 