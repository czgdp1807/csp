import multiprocessing
import os
import os.path
import platform
import subprocess
import sys
from shutil import which
from skbuild import setup

# This will be used for e.g. the sdist
if not os.path.exists("vcpkg"):
    subprocess.call(["git", "clone", "https://github.com/Microsoft/vcpkg.git"])
if not os.path.exists("vcpkg/ports"):
    subprocess.call(["git", "submodule", "update", "--init", "--recursive"])
if not os.path.exists("vcpkg/buildtrees"):
    subprocess.call(["git", "pull"], cwd="vcpkg")
    if os.name == "nt":
        subprocess.call(["bootstrap-vcpkg.bat"], cwd="vcpkg")
        subprocess.call(["vcpkg", "install"], cwd="vcpkg")
    else:
        subprocess.call(["./bootstrap-vcpkg.sh"], cwd="vcpkg")
        subprocess.call(["./vcpkg", "install"], cwd="vcpkg")


python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
cmake_args = [f"-DCSP_PYTHON_VERSION={python_version}"]
vcpkg_toolchain_file = os.path.abspath(
    os.environ.get(
        "CSP_VCPKG_PATH",
        os.path.join("vcpkg/scripts/buildsystems/vcpkg.cmake"),
    )
)

if os.path.exists(vcpkg_toolchain_file):
    cmake_args.extend(
        [
            "-DCMAKE_TOOLCHAIN_FILE={}".format(vcpkg_toolchain_file),
            "-DCSP_USE_VCPKG=ON",
            "-DSnappy_LIB=snappy",
            "-DARROW_WITH_UTF8PROC=Off",
        ]
    )

# if "CONDA_PREFIX" in os.environ:
#     cmake_args.append(f"-DCMAKE_MODULE_PATH={os.environ['CONDA_PREFIX']}/lib/cmake/absl;{os.environ['CONDA_PREFIX']}/lib/cmake/arrow")

if "CMAKE_ARGS" in os.environ:
    # conda
    cmake_args.extend(os.environ["CMAKE_ARGS"].split(" "))

if "CXX" in os.environ:
    cmake_args.append(f"-DCMAKE_CXX_COMPILER={os.environ['CXX']}")

if "DEBUG" in os.environ:
    cmake_args.append("-DCMAKE_BUILD_TYPE=Debug")

if "CSP_MANYLINUX" in os.environ:
    cmake_args.append("-DCSP_MANYLINUX=ON")

if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
    os.environ["CMAKE_BUILD_PARALLEL_LEVEL"] = str(multiprocessing.cpu_count())

if platform.system() == "Darwin":
    os.environ["OSX_DEPLOYMENT_TARGET"] = os.environ.get("OSX_DEPLOYMENT_TARGET", "10.13")
    os.environ["MACOSX_DEPLOYMENT_TARGET"] = os.environ.get("OSX_DEPLOYMENT_TARGET", "10.13")
elif platform.system() == "Windows":
    import distutils.msvccompiler as dm
    # https://wiki.python.org/moin/WindowsCompilers#Microsoft_Visual_C.2B-.2B-_14.0_with_Visual_Studio_2015_.28x86.2C_x64.2C_ARM.29
    msvc = {
        "12": "Visual Studio 12 2013",
        "14": "Visual Studio 14 2015",
        "14.0": "Visual Studio 14 2015",
        "14.1": "Visual Studio 15 2017",
        "14.2": "Visual Studio 16 2019",
        "14.3": "Visual Studio 17 2022",
    }.get(str(dm.get_build_version()), "Visual Studio 15 2017")
    cmake_args.extend(
        [
            "-G",
            os.environ.get("CSP_GENERATOR", msvc),
        ]
    )

if hasattr(platform, "mac_ver") and platform.mac_ver()[0].startswith("14"):
    cmake_args.append("-DCSP_USE_LD_CLASSIC_MAC=ON")

if which("ccache"):
    cmake_args.append("-DCSP_USE_CCACHE=On")

print(f"CMake Args: {cmake_args}")

setup(
    name="csp",
    version="0.0.1",
    packages=["csp"],
    cmake_install_dir="csp",
    cmake_args=cmake_args,
    # cmake_with_sdist=True,
)
