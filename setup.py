from setuptools import setup

setup(
    name="ragetype",
    version="1.0.0",
    description="⌨️ Your keyboard fights back. Detects angry typing and plays escalating sound effects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="RageType",
    py_modules=["ragetype"],
    python_requires=">=3.8",
    install_requires=[
        "pynput>=1.7.0",
        "simpleaudio>=1.0.4",
    ],
    entry_points={
        "console_scripts": [
            "ragetype=ragetype:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
    ],
)
