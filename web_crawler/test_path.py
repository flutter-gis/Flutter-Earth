import os

# Test different path variations
paths_to_test = [
    "gee cat/Earth Engine Data Catalog  _  Google for Developers.html",
    "gee cat/Earth Engine Data Catalog _ Google for Developers.html",
    "../gee cat/Earth Engine Data Catalog  _  Google for Developers.html",
    "../gee cat/Earth Engine Data Catalog _ Google for Developers.html",
]

for path in paths_to_test:
    exists = os.path.exists(path)
    print(f"Path: {path}")
    print(f"Exists: {exists}")
    if exists:
        print(f"Size: {os.path.getsize(path)} bytes")
    print("-" * 50) 