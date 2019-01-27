import info

from Package.CMakePackageBase import *
from Package.AutoToolsPackageBase import *


class subinfo(info.infoclass):
    def setTargets(self):
        self.targets['0.1.9'] = "http://www.mega-nerd.com/SRC/libsamplerate-0.1.9.tar.gz"
        self.targetInstSrc['0.1.9'] = 'libsamplerate-0.1.9'
        self.targetDigests['0.1.9'] = 'ed60f957a4ff87aa15cbb1f3dbd886fa7e5e9566'
        if not CraftCore.compiler.isGCCLike():
            self.patchToApply['0.1.9'] = ('libsamplerate-0.1.9-20180928.diff', 1)
        self.description = "an audio sample rate converter library"
        self.defaultTarget = '0.1.9'

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = None
        self.runtimeDependencies["libs/libsndfile"] = None


if CraftCore.compiler.isGCCLike():
    class Package(AutoToolsPackageBase):
        def __init__(self):
            AutoToolsPackageBase.__init__(self)
            self.subinfo.options.configure.ldflags += "-framework Carbon"
            self.subinfo.options.configure.cflags += "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks/Carbon.framework/Versions/A/Headers/"
            self.subinfo.options.configure.cxxflags += "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/System/Library/Frameworks/Carbon.framework/Versions/A/Headers/"
else:
    class Package(CMakePackageBase):
        def __init__(self):
            CMakePackageBase.__init__(self)
            self.subinfo.options.configure.args = " -DBUILD_SHARED_LIB=ON -DBUILD_EXAMPLES=OFF -DBUILD_TEST=OFF"
