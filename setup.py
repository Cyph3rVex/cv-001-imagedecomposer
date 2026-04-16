from setuptools import setup, find_packages

setup(
    name="cv-001-image-decomposer",
    version="1.0.0",
    description="Professional Image Decomposer and Layer Editor with AI Inpainting",
    author="Cypher Vex",
    author_email="cyphervex@null.net",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "opencv-python-headless",
        "numpy",
        "pytesseract",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
