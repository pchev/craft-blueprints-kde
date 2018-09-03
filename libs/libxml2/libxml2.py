import info
from Package.AutoToolsPackageBase import *
from Package.MakeFilePackageBase import *

class subinfo(info.infoclass):
    def setTargets(self):
        for ver in ['2.9.7']:
            self.targets[ver] = 'ftp://xmlsoft.org/libxml2/libxml2-' + ver + '.tar.gz'
            self.targetInstSrc[ver] = 'libxml2-' + ver
            if not CraftCore.compiler.isGCCLike():
                self.targetInstSrc[ver] = os.path.join(self.targetInstSrc[ver], 'win32')
        self.targetDigests['2.9.7'] = (['f63c5e7d30362ed28b38bfa1ac6313f9a80230720b7fb6c80575eeab3ff5900c'], CraftHash.HashAlgorithm.SHA256)
        self.description = "XML C parser and toolkit (runtime and applications)"
        self.defaultTarget = '2.9.7'

    def setDependencies(self):
        # autoreconf requires pkg-config, but as pkg-config needs xml2 we disabled this dependency
        #self.buildDependencies["dev-utils/pkg-config"] = "default"
        self.runtimeDependencies["virtual/base"] = "default"
        self.runtimeDependencies["libs/zlib"] = "default"
        self.runtimeDependencies["libs/liblzma"] = "default"
        self.runtimeDependencies["libs/iconv"] = "default"
        if CraftCore.compiler.isMinGW():
            self.buildDependencies["dev-utils/msys"] = "default"


class PackageMSVC(MakeFilePackageBase):
    def __init__(self, **args):
        MakeFilePackageBase.__init__(self)
        self.supportsNinja = False
        self.subinfo.options.useShadowBuild = False
        self.subinfo.options.make.supportsMultijob = False

    def configure(self):
        self.enterSourceDir()
        includedir = os.path.join(CraftCore.standardDirs.craftRoot(), 'include')
        libdir = os.path.join(CraftCore.standardDirs.craftRoot(), 'lib')
        prefixdir = self.imageDir()
        builddebug = "yes" if self.buildType() == "Debug" else "no"

        return utils.system([f"cscript.exe",
                            f".\configure.js",
                            f"compiler=msvc",
                            f"include={includedir}",
                            f"lib={libdir}",
                            f"prefix={prefixdir}",
                            f"debug={builddebug}",
                            f"zlib=yes",
                            f"iconv=yes"])

    def install(self):
        if not MakeFilePackageBase.install(self):
            return False
        includedir = os.path.join(self.imageDir(), "include")
        libxmldir = os.path.join(includedir, "libxml2")
        utils.moveDir(os.path.join(libxmldir, "libxml"), includedir) #otherwise it isn't picked up by libxslt
        return True

class PackageMinGW(AutoToolsPackageBase):
    def __init__(self, **args):
        AutoToolsPackageBase.__init__(self)
        self.subinfo.options.configure.args += " --disable-static --enable-shared --without-python "
        if not CraftCore.cache.findApplication("pkg-config"):
            root = CraftCore.standardDirs.craftRoot()
            self.subinfo.options.configure.args += (f" PKG_CONFIG=':'"
                                                    f" --with-zlib='{root}' --with-iconv='{root}' --with-lzma='{root}'")

if CraftCore.compiler.isGCCLike():
    class Package(PackageMinGW):
        def __init__(self):
            PackageMinGW.__init__(self)
else:
    class Package(PackageMSVC):
        def __init__(self):
            PackageMSVC.__init__(self)
