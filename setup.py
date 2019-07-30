import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ultimapy",
    version="0.0.1",
    author="Jack Ward",
    author_email="jackward84@gmail.com",
    description="Ultima SDK Python Port",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jackuoll/ultima-py",
    packages=setuptools.find_packages(),
    license="Beerware",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
