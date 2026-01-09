from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="meowlang",
    version="1.0.0",
    author="MeowLang Team",
    description="Un langage de programmation élégant, félin et francophone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meowlang/meowlang",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "meowlang=meowlang.cli:main",
        ],
    },
    install_requires=[],
)
