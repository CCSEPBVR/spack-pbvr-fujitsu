# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install pbvr
#
# You can edit this file again by typing:
#
#     spack edit pbvr
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

import os
import platform
import re

from llnl.util.filesystem import install_tree

from spack.package import *
from spack.util.environment import set_env

class Pbvr(Package):
    """CS/IS-PBVR is a scientific visualization application designed
    based on Particle-Based Volume Rendering (PBVR). This application
    is capable of multivariate visualization and three-dimensional point cloud visualization
    in addition to standard visualization functions such as volume rendering
    and isosurfaces for 3D volume data obtained from simulations and measuring instruments.
    In addition, the framework for distributed processing of optimized PBVR is characterized
    by the ability to remotely visualize large-scale time-series volume data in remote locations
    at high speed. As a method of remote visualization, you can choose between
    client-server (CS) visualization, which visualizes volume data stored in remote storage,
    and in-situ (IS) visualization, which visualizes simulations simultaneously and
    in the same environment. This application is being developed at the Center
    for Computational Science and e-Systems of the Japan Atomic Energy Agency."""

    phases = ["build", "install"]

    homepage = "https://github.com/CCSEPBVR/CS-IS-PBVR"
    url = "https://github.com/CCSEPBVR/CS-IS-PBVR/archive/refs/tags/v3.4.0.tar.gz"

    maintainers("sakamoto-naohito")

    license("LGPL-3.0-only")

    version("3.5.0", sha256="264c82d9e94b6f8477952ce2f80834332dbc9047db694f7f3ba2ab07c7c92aae")

    variant("client", default=True, description="Build Client Program")
    variant("mpi", default=True, description="Enable MPI Support")
    variant("extended_fileformat", default=True, description="Enable extended fileformat")

    depends_on("mpi", when="+mpi")
    depends_on("qt-base@6.2.4+opengl", when="+client%gcc")
    depends_on("qt-svg-pbvr@6.2.4+widgets", when="+client%gcc")
    depends_on("vtk-pbvr@9.3.1~mpi", when="~mpi%gcc")
    depends_on("vtk-pbvr@9.3.1+mpi", when="+mpi%gcc")
    depends_on("freeglut", when="%gcc")

    patch("kvs-conf.patch", when="~client~extended_fileformat%gcc")
    patch("kvs-extended-fileformat-conf.patch", when="~client+extended_fileformat%gcc")
    patch("kvs-client-conf.patch", when="+client~extended_fileformat%gcc")
    patch("kvs-client-extended-fileformat-conf.patch", when="+client+extended_fileformat%gcc")

    patch("pbvr-fujitsu-conf.patch", when="~mpi%fj")
    patch("pbvr-fujitsu-conf-mpi.patch", when="+mpi%fj")
    patch("makefile-machine-fujitsu-omp.patch", when="~mpi%fj")
    patch("makefile-machine-fujitsu-mpi-omp.patch", when="+mpi%fj")
    patch("pbvr-conf.patch", when="~mpi%gcc")
    patch("pbvr-conf-mpi.patch", when="+mpi%gcc")
    patch("makefile-machine-gcc-omp.patch", when="~mpi%gcc")
    patch("makefile-machine-gcc-mpi-omp.patch", when="+mpi%gcc")

    def patch(self):
        source_dir = self.stage.source_path
        for root, dirs, files in os.walk(source_dir):
            for fname in files:
                path = os.path.join(root, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "KVS_DIR" in content:
                        filter_file("KVS_DIR", "SPACK_KVS_DIR", path)
                except Exception:
                    pass

    def build(self, spec, prefix):
        if spec.compiler.name == "gcc":
            with set_env(
                KVS_CPP="g++",
                SPACK_KVS_DIR=prefix,
                VTK_VERSION="9.3",
                VTK_INCLUDE_PATH=str(spec["vtk-pbvr"].prefix.include) + "/vtk-9.3",
                VTK_LIB_PATH=str(spec["vtk-pbvr"].prefix.lib),
            ):
                # Build KVS
                build_dir = join_path(self.stage.source_path, "KVS")
                with working_dir(build_dir):
                    make()
                    make("install")

                # Build Client
                if "+client" in spec:
                    qmake = Executable(spec["qt-base"].prefix.bin.qmake)
                    build_dir = join_path(self.stage.source_path, "Client/build")
                    os.makedirs(build_dir)
                    with working_dir(build_dir):
                        qmake("../pbvr_client.pro")
                        make()

                # Build Sevrer
                make("-C", "CS_server")
        elif spec.compiler.name == "fj":
            # Build Server
            make("-C", "CS_server")

    def install(self, spec, prefix):
        mkdirp(prefix.bin)
        install("CS_server/pbvr_server", prefix.bin)
        install("CS_server/Filter/pbvr_filter", prefix.bin)

        if spec.compiler.name == "gcc":
            install("CS_server/KVSMLConverter/Example/Release/kvsml-converter", prefix.bin)

            if "+client" in spec:
                install("Client/build/App/pbvr_client", prefix.bin)
                src = self.stage.source_path
                install_tree(os.path.join(src, "Client/build/App/Shader"), os.path.join(prefix.bin, "Shader"))
                install_tree(os.path.join(src, "Client/build/App/Font"), os.path.join(prefix.bin, "Font"))
