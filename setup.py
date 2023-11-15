"""Installation file for ansys-mapdl-reader"""
from io import open as io_open
import os

import numpy as np
from setuptools import Extension, setup

if os.name == "nt":  # windows
    extra_compile_args = ["/openmp", "/O2", "/w", "/GS"]
elif os.name == "posix":  # linux/mac os
    extra_compile_args = ["-O3", "-w"]


# Get version from version info
__version__ = None
this_file = os.path.dirname(__file__)
version_file = os.path.join(this_file, "ansys", "mapdl", "reader", "_version.py")
with io_open(version_file, mode="r") as fd:
    # execute file from raw string
    exec(fd.read())


setup(
    name="ansys-mapdl-reader",
    packages=["ansys.mapdl.reader", "ansys.mapdl.reader.examples"],
    version=__version__,
    description="Pythonic interface to files generated by MAPDL",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="Ansys, Inc.",
    author_email="pyansys.maintainers@ansys.com",
    maintainer="PyAnsys developers",
    maintainer_email="pyansys.maintainers@ansys.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    url="https://github.com/pyansys/pymapdl-reader",
    # Build cython modules
    # cmdclass={"build_ext": build_ext},
    include_dirs=[np.get_include()],
    ext_modules=[
        Extension(
            "ansys.mapdl.reader._archive",
            [
                "ansys/mapdl/reader/cython/_archive.pyx",
                "ansys/mapdl/reader/cython/archive.c",
            ],
            extra_compile_args=extra_compile_args,
            language="c",
        ),
        Extension(
            "ansys.mapdl.reader._reader",
            [
                "ansys/mapdl/reader/cython/_reader.pyx",
                "ansys/mapdl/reader/cython/reader.c",
                "ansys/mapdl/reader/cython/vtk_support.c",
            ],
            extra_compile_args=extra_compile_args,
            language="c",
        ),
        Extension(
            "ansys.mapdl.reader._relaxmidside",
            ["ansys/mapdl/reader/cython/_relaxmidside.pyx"],
            extra_compile_args=extra_compile_args,
            language="c",
        ),
        Extension(
            "ansys.mapdl.reader._cellqual",
            ["ansys/mapdl/reader/cython/_cellqual.pyx"],
            extra_compile_args=extra_compile_args,
            language="c",
        ),
        Extension(
            "ansys.mapdl.reader._binary_reader",
            [
                "ansys/mapdl/reader/cython/_binary_reader.pyx",
                "ansys/mapdl/reader/cython/binary_reader.cpp",
            ],
            extra_compile_args=extra_compile_args,
            language="c++",
        ),
    ],
    python_requires=">=3.7,<4",
    keywords="vtk MAPDL ANSYS cdb full rst",
    package_data={
        "ansys.mapdl.reader.examples": [
            "TetBeam.cdb",
            "HexBeam.cdb",
            "file.rst",
            "file.full",
            "sector.rst",
            "sector.cdb",
        ]
    },
    install_requires=[
        "appdirs>=1.4.0",
        "matplotlib>=3.0.0",
        "numpy>=1.16.0",
        "pyvista>=0.32.0",
        "tqdm>=4.45.0",
        "vtk>=9.0.0",
    ],
)
