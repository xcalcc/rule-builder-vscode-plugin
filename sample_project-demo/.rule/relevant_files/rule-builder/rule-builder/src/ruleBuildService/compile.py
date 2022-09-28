"""
compilation of rule file source code to
.udr/.o/.a files
"""
import os
import time
import subprocess
import glob
from common.XcalException import XcalException
from common.XcalLogger import XcalLogger
from ruleBuildService.config import ErrorNo
from shutil import copy


class Compile:
    """compilation class

    Args:
        lang (str): target language
        target_dir (str): path to the directory where the files are located
        xvsa_home (str); path to xvsa directory
    Attributes:
        lang (str): taret language
        target_dir (str): path to the directory where the files are located
        xvsa_home (str); path to xvsa directory
    """
    def __init__(self, lang, target_dir, xvsa_home):
        self.lang = lang
        self.target_dir = target_dir
        self.xvsa_home = xvsa_home
        self.logger = XcalLogger("Compile", "__init__")

    def _get_files_with_ext(self, in_dir, ext):
        """get all files with extension (.ext) from directory recursively.

        Args:
            in_dir (str): path to input directory
            ext (str): finding the extnesion
        Returns:
            list: list of path to the requested files with extension
        """
        #return [i.name for i in Path(in_dir).rglob('*.%s' % ext)]
        return glob.glob("%s/**/*.%s"%(in_dir, ext), recursive=True)

    def compile_files(self, files):
        """compiling all files

            Args:
                files (str): path to source files
        """
        paths = []
        # validate files
        for f in files:
            tmp = os.path.realpath(f)
            if not os.path.exists(tmp):
                raise XcalException("Compile", "compile_files",\
                        "file: %s not found" % f,
                        err_code = ErrorNo.E_RESOURCE_NOT_FOUND)
            paths.append(tmp)

        # check xvsa_home
        if not os.path.exists(os.path.join(self.xvsa_home, 'bin/xvsa')):
            raise XcalException("Compile", "compile_files",
                                "xvsa not found on %s" % self.xvsa_home,
                                ErrorNo.E_RESOURCE_NOT_FOUND)

        if self.lang == 'java':
            self._compile_java(paths)
        elif self.lang == 'c' or self.lang == 'c++':
            self._compile_c(paths)
        else:
            raise XcalException("Compile", "compile_files",
                                "language not recognised: %s" % self.lang,
                                err_code = ErrorNo.E_LANGUAGE_NOT_SUPPORTED)

    def _compile_c(self, paths):
        """compile c files

        Args:
            paths (str): list of path
        """
        self.logger.debug("_compile_c", "compiling c source files")
        rbc_engine_src = os.path.join(self.xvsa_home, 'include/rbc_base.h')
        copy(rbc_engine_src, self.target_dir)
        for sub_dir in os.scandir(self.target_dir): # copy rbc_engine_src to subdirectories
            if sub_dir.is_dir():
                copy(rbc_engine_src, sub_dir.path)
        current = os.path.realpath(os.curdir)
        os.chdir(self.target_dir) # change current directory
        self.logger.debug("_compile_c", "current dir: %s" % os.path.realpath(os.curdir))
        cxx_files = self._get_files_with_ext(os.curdir, "cxx")
        gcc_cmd = "gcc -g -c %s" % " ".join(cxx_files)
        gcc = subprocess.call(gcc_cmd, shell=True)
        if gcc: #gcc return 0 if compile success
            raise XcalException("Compile", "_compile_c", "compiling C failure",
                                err_code=ErrorNo.E_XVSA_COMPILE_ERROR)
        
        self.logger.debug("_compile_c", "gcc command: %s" % gcc_cmd)

        # compile each of the .cxx files to .o file
        for file in cxx_files:
            f_name = file[2:-4] # extract name, all cxx files in form ./<name>.cxx
            xvsa_script = os.path.join(self.xvsa_home, 'bin/xvsa')
            xvsa_cmd = "%s -c -Ww,-RBC %s.cxx -o %s.o" % (xvsa_script, f_name, f_name)
            self.logger.debug("_compile_c", "xvsa command: %s" % xvsa_cmd)
            xvsa = subprocess.call(xvsa_cmd, shell=True)

            if xvsa:
                raise XcalException("Compile", "_compile_c", "xvsa compilation failure",
                                    err_code=ErrorNo.E_XVSA_COMPILE_ERROR)

        os.chdir(current)
        
    def _compile_java(self, paths):
        """compile java files

        Args:
            paths (str): list of path
        """
        self.logger.debug("_compile_java", "compiling java source files")
        rbc_engine_src = os.path.join(self.xvsa_home, 'include/RBC_ENGINE.java')
        copy(rbc_engine_src, self.target_dir)
        current = os.path.realpath(os.curdir)
        os.chdir(self.target_dir) # change current directory
        self.logger.debug("_compile_java", "current dir: %s" % os.path.realpath(os.curdir))
        java_files = self._get_files_with_ext(os.curdir, "java")
        javac_cmd = "javac -g -d . %s" % " ".join(java_files)
        javac = subprocess.call(javac_cmd, shell=True)
        if javac:
            raise XcalException("Compile", "_compile_java", "compiling java failure",
                                err_code=ErrorNo.E_XVSA_COMPILE_ERROR)
        class_files = self._get_files_with_ext(os.curdir, "class")
        # if string contains $ -> turn to \$
        class_files = [i.replace('$','\$') for i in class_files] # $ interpreted as variable
        self.logger.debug("_compile_java", "javac command: %s" % javac_cmd)
        self.logger.debug("_compile_java", "class files: %s" % class_files)

        jar_cmd = "jar cf lib.jar %s" % " ".join(class_files)
        self.logger.debug("_compile_java", "jar command: %s" % jar_cmd)
        jar = subprocess.call(jar_cmd, shell=True)
        if jar:
            raise XcalException("Compile", "_compile_java", "jar compilation failure",
                                err_code=ErrorNo.E_XVSA_COMPILE_ERROR)
        xvsa_script = os.path.join(self.xvsa_home, 'bin/xvsa')
        xvsa_cmd = "%s -noinline -Wf,-RBC=true -c -o lib.o lib.jar" % xvsa_script
        self.logger.debug("_compile_java", "xvsa command: %s" % xvsa_cmd)
        xvsa = subprocess.call(xvsa_cmd, shell=True)

        if xvsa:
            raise XcalException("Compile", "_compile_java", "xvsa compilation failure",
                                err_code=ErrorNo.E_XVSA_COMPILE_ERROR)

        # archiving the file to .udr
        # archive = subprocess.call("ar cr user_rule.udr lib.o", shell=True)
        # if archive:
            # raise XcalException("Compile", "_compile_java", "archiving failure",
                                # err_code=ErrorNo.E_XVSA_COMPILE_ERROR)
        os.chdir(current)

    def compile_jar(self, paths):
        """turning jar files into .o file 

        use mapfej to turn jar into .o, can further be processed to 
        .udr. Make sure to put the main jar file in the first index
        
        Args:
            paths (list): list of path to .jar files to be put together.
        """
        if not paths: # empty
            self.logger.warn("compile_jar", "No dependency passed")
            return
        self.logger.info("compile_jar", "references passed: %s" % paths)
        xvsa_script = os.path.join(self.xvsa_home, 'bin/xvsa')
        for f in paths:
            if not os.path.exists(f):
                raise XcalException("Compile", "compile_jar", "file: %s not found" % f,
                                    err_code=ErrorNo.E_RESOURCE_NOT_FOUND)
        main_jar = paths[0]
        target_out = os.path.join(self.target_dir, "depn.o")
        cmd = "%s -c -noinline -Wf,-VTABLE=true -o %s %s" % (xvsa_script, target_out, main_jar)
        if len(paths) > 1: # more than one
            for f in paths[1:]:
                cmd += " -Wf,-cp=%s" % f

        self.logger.debug("compile_jar", "command: %s" % cmd)
        comp = subprocess.call(cmd, shell=True)
        if comp:
            raise XcalException("Compile", "compile_jar", "compiling jar failure",
                                err_code=ErrorNo.E_XVSA_COMPILE_ERROR)

    def archive_files(self, path, out_f='user_rule.udr'):
        """archiving .o files to .udr

        if java, look into lib.o and depn.o (if any) to convert to .udr.
        if C, look into .o files (if any) to convert to .udr.

        Args:
            path (str): path to output
        """
        self.logger.debug("archive_files", "archiving files")
        if not os.path.exists(path):
            raise XcalException("Compile", "archive_files", "path: %s not found" % path,
                                err_code=ErrorNo.E_RESOURCE_NOT_FOUND)

        if self.lang == 'java':
            self._archive_java(path, out_f)
        elif self.lang == 'c'  or self.lang == 'c++':
            self._archive_c(path, out_f)
        else:
            raise XcalException("Compile", "archive_files",
                                "language not recognised: %s" % self.lang,
                                err_code = ErrorNo.E_LANGUAGE_NOT_SUPPORTED)

    def _archive_java(self, path, out_f='user_rule.udr'):
        lib_o = os.path.join(path, 'lib.o')
        depn_o = os.path.join(path, 'depn.o')

        if not(os.path.exists(lib_o) or os.path.exists(depn_o)):
            self.logger.warn("archive_files", "nothing to archive")
            return

        target_out_f = os.path.join(self.target_dir, out_f)
        cmd = "ar cr %s %s" % (target_out_f, lib_o)
        if os.path.exists(depn_o):
            cmd += " %s" % depn_o
        
        self.logger.debug("archive command", cmd)
        archive = subprocess.call(cmd, shell=True)
        if archive:
            raise XcalException("Compile", "archive_files", 
                                "archiving failure",
                                ErrorNo.E_XVSA_COMPILE_ERROR)

    def _archive_c(self, path, out_f='user_rule.udr'):
        o_files = self._get_files_with_ext(os.curdir, "o")
        if not o_files:
            self.logger.warn("archive_files", "nothing to archive")
            return
        print("ALL FILES",o_files)
        target_out_f = os.path.join(self.target_dir, out_f)
        cmd = "ar cr %s %s" % (target_out_f, " ".join(o_files))
        
        self.logger.debug("archive command", cmd)
        archive = subprocess.call(cmd, shell=True)
        if archive:
            raise XcalException("Compile", "archive_files", 
                                "archiving failure",
                                ErrorNo.E_XVSA_COMPILE_ERROR)