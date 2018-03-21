import sys

import info

class subinfo(info.infoclass):
    def setTargets(self):
        self.versionInfo.setDefaultValues()
        self.description = "python support for kdevelop"

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = "default"
        self.runtimeDependencies["extragear/kdevelop/kdevelop"] = "default"
        self.runtimeDependencies["extragear/kdevelop/kdev-php"] = "default"

from Package.CMakePackageBase import *


class Package(CMakePackageBase):
    def __init__(self):
        CMakePackageBase.__init__(self)
        self.subinfo.options.configure.args = f" -DPYTHON_EXECUTABLE=\"{sys.executable}\""
