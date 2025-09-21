from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Lithium-Validation",
    version="1.0.0",
    author="Guillermo Espinosa",
    author_email="hola@ged.do",
    description="AI output validation framework based on hallucination research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GED-DO/Lithium-Validation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    install_requires=["mcp>=1.0.0"],
    entry_points={
        "console_scripts": [
            "lithium-validate=lithium_validation.cli.validate:main",
        ],
    },
)
