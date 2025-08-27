"""
Setup configuration for Paper to Voice Assistant
"""

from setuptools import setup, find_packages

with open("README_NEW.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="paper-to-voice-assistant",
    version="1.0.0",
    author="Paper-to-Voice Team",
    author_email="your.email@example.com",
    description="Convert research papers into engaging podcast audio using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/priyanshiranawat15/Paper-to-voice-assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "paper-to-voice=paper_to_voice.main:main",
        ],
    },
)
