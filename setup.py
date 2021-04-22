import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ultimapy",
    version="0.0.22",
    author="Jack Ward",
    author_email="jackward84@gmail.com",
    description="UltimaPy - Extract information and images from the UO client files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jackuoll/ultima-py",
    packages=setuptools.find_packages(),
    license="Beerware",
    install_requires=[
        'Pillow',
        'imageio'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
