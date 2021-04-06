import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bobby-home",
    version="0.4.0",
    author="Maxime Moreau",
    author_email="contact@maxime-moreau.fr",
    description="Home security system with RaspberryPi's.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mxmaxime/mx-tech-house",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Intended Audience :: Developers"
    ],
    python_requires='>=3.8',
)
