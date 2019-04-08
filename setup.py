import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Pycle",
    version="0.0.2",
    author="John Wong",
    author_email="john-wong@outlook.com",
    description="a Commandline Utility for zabbix",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://none",
    packages=setuptools.find_packages(),
    install_requires=[
        'Click',
        'cx-Oracle'
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pycle=pycle.pycle:main',
        ],
    }
)