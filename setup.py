"""
Setup script for ORDIS-A.I.
"""

from setuptools import setup, find_packages
import os

def read_requirements():
    """Read requirements from requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

def read_long_description():
    """Read README for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "ORDIS-A.I. - A customizable AI assistant"

setup(
    name="ordis-ai",
    version="1.0.0",
    author="Ephraim Chapin",
    author_email="ephraim@example.com",
    description="A customizable AI assistant inspired by Claude Code",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/ephraim-chapin/ordis-ai",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ordis=ordis_ai.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
