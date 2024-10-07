import pathlib
import setuptools

setuptools.setup(
    name='funflow',
    version='0.0.2',
    description='Powerful dataflow programming library',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ermike98/FunFlow',
    author='Save',
    author_email='michelangelo.saveriano.1998@gmail.com',
    license='MIT',
    project_urls={
        "Documentation": "https://github.com/Ermike98/FunFlow",
        "Source": "https://github.com/Ermike98/FunFlow",
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities"
    ],
    python_requires='>=3.8',
    install_requires=[],
    extras_require={
        "vis": ["networkx", "graphviz"]
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
)