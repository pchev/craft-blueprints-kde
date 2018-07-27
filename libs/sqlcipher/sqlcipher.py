# -*- coding: utf-8 -*-
# Copyright 2018 Łukasz Wojniłowicz <lukasz.wojnilowicz@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import info
import CraftCore
from Package.AutoToolsPackageBase import *
from Package.MSBuildPackageBase import *

class subinfo(info.infoclass):
    def setTargets(self):
        for ver in ['3.4.2']:
            self.targets[ver] = 'https://github.com/sqlcipher/sqlcipher/archive/v%s.zip' % ver
            self.archiveNames[ver] = "sqlcipher-%s.zip" % ver
            self.targetInstSrc[ver] = 'sqlcipher-%s' % ver
            self.patchLevel[ver] = 2

        self.targetDigests["3.4.2"] = (['f2afbde554423fd3f8e234d21e91a51b6f6ba7fc4971e73fdf5d388a002f79f1'], CraftHash.HashAlgorithm.SHA256)

        if CraftCore.compiler.isWindows:
            self.patchToApply["3.4.2"] = [("sqlcipher-3.4.2-20180727.diff", 1)]

        self.defaultTarget = "3.4.2"

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = "default"
        self.runtimeDependencies["libs/openssl"] = "default"
        self.runtimeDependencies["libs/tcl"] = "default"
        if CraftCore.compiler.isMinGW():
            self.buildDependencies["dev-utils/msys"] = "default"

#warning: empty sqlite3.h can prevent successfull build
class PackageAutotools(AutoToolsPackageBase):
    def __init__(self, **args):
        AutoToolsPackageBase.__init__(self)
        if CraftCore.compiler.isMinGW():
            self.subinfo.options.make.supportsMultijob = False
            self.subinfo.options.configure.args += " --disable-static --enable-shared --enable-tempstore=yes CFLAGS='-DSQLITE_HAS_CODEC -I%s' " % OsUtils.toMSysPath(os.path.join(CraftCore.standardDirs.craftRoot(), "include"))
        else:
            self.subinfo.options.configure.args += " --disable-static --enable-shared --enable-tempstore=yes CFLAGS='-DSQLITE_HAS_CODEC' "

    def install(self):
        if CraftCore.compiler.isMinGW():
            fileName = os.path.join(self.buildDir(), "Makefile")
            with open(fileName, "rt") as f:
                content = f.read()
            content = content.replace("$(DESTDIR)", "") # otherwise install path looks like e.g. /m/image-RelWithDebInfo-3.4.2/m/lib because install path = $(DESTDIR)$(libdir)
            with open(fileName, "wt") as f:
                f.write(content)

        return super().install()

    def postInstall(self):
        if CraftCore.compiler.isMinGW():
            cmakes = [ os.path.join(CraftCore.standardDirs.craftRoot(), "lib" , "pkgconfig", "sqlcipher.pc")]
        else:
            cmakes = []
        return self.patchInstallPrefix(cmakes,
                                        OsUtils.toMSysPath(self.subinfo.buildPrefix)[:-1],
                                        OsUtils.toUnixPath(CraftCore.standardDirs.craftRoot()[:-1]))

class PackageMSVC(MSBuildPackageBase):
    def __init__(self, **args):
        MSBuildPackageBase.__init__(self)

    def configure(self):
        self.enterSourceDir()
        fileName = "Makefile.msc"
        with open(fileName, "rt") as f:
            content = f.read()

        # recipe taken from https://github.com/sqlitebrowser/sqlitebrowser/wiki/Win64-setup-%E2%80%94-Compiling-SQLCipher

        # libname_EXPORTS is cmake variable. It allows to use __declspec(dllexport) while building this library
        # and __declspec(dllimport) while linking to this library
        defines = ("TCC = $(TCC) -DSQLITE_HAS_CODEC -Dlibsqlcipher_EXPORTS\n"
                   "RCC = $(RCC) -DSQLITE_HAS_CODEC -Dlibsqlcipher_EXPORTS\n")

        includeDir = os.path.join(CraftCore.standardDirs.craftRoot() , "include")
        includeDirs = (f"TCC = $(TCC) -I{includeDir}\n"
                       f"RCC = $(RCC) -I{includeDir}\n")

        index = content.find("TCC = $(TCC) -DSQLITE_TEMP_STORE=1")
        content = content[:index] + defines + includeDirs + content[index:]

        libDir = os.path.join(CraftCore.standardDirs.craftRoot() , "lib")
        includeLibs = (f"LTLIBPATHS = $(LTLIBPATHS) /LIBPATH:{libDir}\n"
                        "LTLIBS = $(LTLIBS) libssl.lib libcrypto.lib tcl86.lib\n")

        index = content.find("# If ICU support is enabled, add the linker options for it.")
        content = content[:index] + includeLibs + content[index:]

        content = content.replace(r"-DSQLITE_TEMP_STORE=1", r"-DSQLITE_TEMP_STORE=2")
        content = content.replace(r"winsqlite3.dll", r"sqlcipher.exe")
        content = content.replace(r"winsqlite3.lib", r"sqlcipher.lib")
        content = content.replace(r"winsqlite3shell.exe", r"sqlcipher.exe")
        content = content.replace(r"sqlite3.dll", r"sqlcipher.dll")
        content = content.replace(r"sqlite3.lib", r"sqlcipher.lib")
        content = content.replace(r"sqlite3.exe", r"sqlcipher.exe")
        content = content.replace(r"sqlite3sh.pdb", r"sqlciphersh.pdb")
        content = content.replace(r"sqlite3.def", r"sqlcipher.def")

        with open(fileName, "wt") as f:
            f.write(content)
        return super().configure()

    def make(self):
        return utils.system(r"nmake -f Makefile.msc")

    def install(self):
        isInstalled = super().install()
        if isInstalled:
            # move sqlcipher headers to sqlcipher directory to not conflit with sqlite3
            includeDir = os.path.join(self.installDir(), "include")
            utils.moveDir(includeDir, os.path.join(self.installDir(), "sqlcipher") )
            utils.createDir(includeDir)
            utils.moveDir(os.path.join(self.installDir(), "sqlcipher"), os.path.join(includeDir, "sqlcipher"))

            # allow finding sqlcipher library by pkgconfig module
            pkgConfigDir = os.path.join(self.installDir(), "lib", "pkgconfig")
            pkgConfigFile = fileName = os.path.join(pkgConfigDir, "sqlcipher.pc")
            utils.createDir(pkgConfigDir)
            utils.copyFile(os.path.join(self.sourceDir(), "sqlcipher.pc.in"), pkgConfigFile)
            with open(pkgConfigFile, "rt") as f:
                content = f.read()
            content = content.replace(r"@prefix@", CraftCore.standardDirs.craftRoot())
            content = content.replace(r"@exec_prefix@", r"${prefix}/bin")
            content = content.replace(r"@libdir@", r"${prefix}/lib")
            content = content.replace(r"@includedir@", r"${prefix}/include")

            with open(pkgConfigFile, "wt") as f:
                f.write(content)

        return isInstalled


if CraftCore.compiler.isGCCLike():
    class Package(PackageAutotools):
        def __init__(self):
            PackageAutotools.__init__(self)
else:
    class Package(PackageMSVC):
        def __init__(self):
            PackageMSVC.__init__(self)
