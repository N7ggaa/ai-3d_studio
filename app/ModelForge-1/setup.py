from setuptools import setup, find_packages

setup(
    name="modelforge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24',
        'trimesh>=3.23',
        'Pillow>=9.5',
        'pygltflib>=1.14.0',
        'opencv-python>=4.7.0',
        'yt-dlp>=2023.3.4',
        'tqdm>=4.65.0',
        'flask>=2.0.0',
        'flask-sqlalchemy>=2.5.0',
        'flask-cors>=3.0.0',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.json', '*.glb', '*.gltf', '*.bin'],
    },
    entry_points={
        'console_scripts': [
            'modelforge=app:main',
        ],
    },
)
