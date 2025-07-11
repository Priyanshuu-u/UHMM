from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tableau_to_powerbi",
    version="0.1.0",
    author="Priyanshuu-u",
    author_email="your.email@example.com",
    description="Automated Tableau to Power BI conversion tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tableau_to_powerbi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "lxml>=4.6.0",
        "pandas>=1.1.0",
        "numpy>=1.19.0",
    ],
    entry_points={
        "console_scripts": [
            "tableau2powerbi=tableau_to_powerbi.cli:main",
        ],
    },
)