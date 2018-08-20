import info


class subinfo(info.infoclass):
    def setTargets( self ):

        for ver in ["0.7.4"]:
            self.targets[ver] = f"http://downloads.sourceforge.net/libdmtx/libdmtx-{ver}.tar.bz2"
            self.targetInstSrc[ver] = f"libdmtx-{ver}"

        self.targetDigests["0.7.4"] = (['b62c586ac4fad393024dadcc48da8081b4f7d317aa392f9245c5335f0ee8dd76'], CraftHash.HashAlgorithm.SHA256)

        self.patchToApply["0.7.4"] = [("libdmtx-0.7.4-20180820.diff", 1)]

        self.description = "libdmtx is open source software for reading and writing Data Matrix barcodes on Linux, Unix, OS X, Windows, and mobile devices. At its core libdmtx is a native shared library, allowing C/C++ programs to use its capabilities without extra restrictions or overhead."
        self.defaultTarget = "0.7.4"

    def setDependencies( self ):
        self.buildDependencies["dev-utils/msys"] = "default"
        self.runtimeDependencies["virtual/base"] = "default"

from Package.AutoToolsPackageBase import *

class Package(AutoToolsPackageBase):
    def __init__( self, **args ):
        AutoToolsPackageBase.__init__( self )
        self.subinfo.options.configure.args = "--enable-static=no --enable-shared=yes"
