#!/bin/bash

fn=$(basename $0)
# use -xfa option even if the parameter of xvsa_scan used with -no-xfa
common_scan_options="-json -msgid -xfa ${SCAN_EXTRA_OPTIONS}"
order_options="-VSA:authen=1"
scan_c_ext_option="-VSA:certc=1 -VSA:zero_global=0"
# Msf, Uaf, Dbf are skipped for now
scan_java_option="-VSA:exp=1 -VSA:certj=1 -VSA:new_npd=1 -VSA:uiv=0 -VSA:uaf=0 -VSA:msf=0 -VSA:dbf=0 -VSA:ral=0"
scan_java_jfe_option="-Wf,-logLevel=INFO -Wf,-allow-phantom-refs=true ${SCAN_EXTRA_JFE_OPTION}"
scan_java_jfe_vtable_option="-Wf,-libGenOnly=true -Wf,-VTABLE=true ${SCAN_EXTRA_VTABLE_OPTION}"
scan_java_skip_vtable="${SCAN_EXTRA_SKIP_VTABLE_OPTION:-YES}"
scan_cross_file=1
scan_token=
scan_server=
scan_mode="normal_scan"
scan_ret=0
skip_jfe_error="${SCAN_EXTRA_SKIP_ERROR}"
objects_file_name="objects_file"

echo "INFO:$0 XVSA-scan script version 0.0.11"

echo "Detecting JAVA_HOME ... ${JAVA_HOME}"
if [ -n "${JAVA_HOME}" ] && [ -d "${JAVA_HOME}" ]; then
  echo "JAVA_HOME is present, continuing ... ok"
elif [ -d /usr/lib/jvm/java-8-openjdk-amd64 ]; then
  export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"
  echo "Using default JAVA_HOME = ${JAVA_HOME}"
else
  echo "Didn't found JAVA_HOME, continue on..."
fi

usage() {
  echo "Usage:"
  echo "  $fn <preprocess_files> -token <token> -server <server> <-xfa> <-no-xfa>"
  echo "  Note: cross file scan is enabled by default."
  echo "        must provide scan token and scan server option when xvsa is ready to accept them."
  echo "        use '-xfa' to enable cross file scan. this option is on by default."
  echo "        use '-no-xfa' to disable cross file scan."
}

prescan_start() {
  echo "pre-scan start time = $(date)"
  prepare_start_time=$(date +%s)
}

prescan_end() {
  prepare_end_time=$(date +%s)
  echo "pre-scan spent : " $((prepare_end_time - prepare_start_time)) " seconds "
}

module_scan_start() {
  echo "Module $1 cross file scan start time = $(date)"
  module_scan_start_time=$(date +%s)
}

module_scan_end() {
  module_scan_end_time=$(date +%s)
  echo "Module $1 cross-file-scan spent : " $((module_scan_end_time - module_scan_start_time)) " seconds "
}

scan_start() {
  echo "Starting scan at $(date)"
  whole_start_time=$(date +%s)
}

scan_end() {
  whole_end_time=$(date +%s)
  echo "Finishing scan at $(date)"
  echo "Scan spent : " $((whole_end_time - whole_start_time)) " seconds "
}

if [ $# -eq 0 ]; then
  usage
  exit 1
fi
until [ $# -eq 0 ]; do
  case "$1" in
  -xfa)
    scan_cross_file=1
    shift
    ;;
  -no-xfa)
    scan_cross_file=0
    shift
    ;;
  -token)
    if [ -n "$2" ]; then
      scan_token=$2
    else
      echo "$fn: missing operand after '$1' "
      usage
      exit 1
    fi
    shift 2
    ;;
  -server)
    if [ -n "$2" ]; then
      scan_server=$2
    else
      echo "$fn: missing operand after '$1' "
      usage
      exit 1
    fi
    shift 2
    ;;
  *)
    # The preprocess.tar.gz will be decompressed to the Preprocess_files folder
    preprocess_files=$1
    if [ -f $1/java.scan/xcalibyte.properties ]; then
      echo "Using Java Scanning ..."
      scan_mode="java_scan"
      if [ -f $1/xcalibyte.properties ]; then
        scan_mode="new_java_scan"
      fi
      shift
    elif [ ! -f "$1/xcalibyte.properties" ]; then
      echo "Warning: no input file dir"
      usage
      exit 1
    else
      shift
    fi
    ;;
  esac
done

create_dir() {
  dir=$1
  rm -rf $dir
  mkdir -p $dir
  if [ $? -ne 0 ]; then
    echo "create directory error!"
    exit 11
  fi
}

cur_dir=$(pwd)
preprocess_files=$(
  cd ${preprocess_files}
  pwd
)
log_dir=$cur_dir/.scan_log
create_dir $log_dir
scan_log=$log_dir/scan.log
performance_log=$log_dir/perf.log
dep_log=$log_dir/depend_list
scan_failed=$log_dir/scan_failed_list
scan_result=$cur_dir/scan_result
create_dir $scan_result

set_value() {
  var=${1%%=*}
  tmp=$(echo $@ | awk -F "${var}=" '{print$NF}' | sed 's/\"//g')
  if [ -n "$tmp" ]; then
    eval $var='$tmp'
  fi
}

init() {
  target=
  if [ -n "$1" ]; then
    init
    target=$1
  fi
  properties="${preprocess_files}/$target/xcalibyte.properties"
  if [ -f "$properties" ]; then
    while read -r line; do
      case "$line" in
      version=*)
        set_value $line
        ;;
      project=*)
        set_value $line
        ;;
      build_root_dir=*)
        set_value $line
        ;;
      build_command=*)
        set_value $line
        ;;
      configure_command=*)
        set_value $line
        ;;
      vcs_tool=*)
        set_value $line
        ;;
      vcs_url=*)
        set_value $line
        ;;
      vcs_token=*)
        set_value $line
        ;;
      vcs_branch=*)
        set_value $line
        ;;
      vcs_version=*)
        set_value $line
        ;;
      src_root_dir=*)
        set_value $line
        ;;
      build_root_dir=*)
        set_value $line
        ;;
      cxx_scan_options=*)
        set_value $line
        ;;
      c_scan_options=*)
        set_value $line
        ;;
      compile_only=*)
        set_value $line
        ;;
      vtable_only=*)
        set_value $line
        ;;
      esac
    done <$properties
  fi
}

# handle preprocess file, generate .o files first.
handle_preprocess_file() {
  for target in $targets; do
    init $target
    pre_dir="${preprocess_files}/$target/preprocess"
    if [ -d "$pre_dir" ]; then
      echo "===========================================================================" >>$scan_log
      echo "### handle preprocess files for $target ......" | tee -a $scan_log
      ### FIXME: Possible error when iterating over folder names containing spaces.
      for file in $(ls $pre_dir); do
        case "$file" in
        *.i | *.ii)
          echo "# NOTE: preprocess xvsa specific pragmas" >>$scan_log
          sed -i 's/#pragma xvsa range/\_\_builtin\_xvsa\_range/g;s/\_\_builtin\_xvsa\_range(.*)/&;/g' $pre_dir/$file
          sed_ret=$?
          [ $sed_ret -ne 0 ] && echo "$pre_dir/$file range pragma preprocess failed" >>$scan_failed
          sed -i 's/#pragma xvsa not\_equal/\_\_builtin\_xvsa\_ne/g;s/\_\_builtin\_xvsa\_ne(.*)/&;/g' $pre_dir/$file
          sed_ret=$?
          [ $sed_ret -ne 0 ] && echo "$pre_dir/$file ne pragma preprocess failed" >>$scan_failed
          if [ "${file##*.}" = "i" ]; then
            comp_option=$c_scan_options
          else
            comp_option=$cxx_scan_options
          fi
          basename=${file%.*}
          obj_options="-o $pre_dir/${basename}.o -c"
          echo "# command: xvsa $common_scan_options $scan_c_ext_option $comp_option $obj_options $pre_dir/$file" >>$scan_log
          xvsa $common_scan_options $order_options $scan_c_ext_option $comp_option $obj_options $pre_dir/$file >>$scan_log 2>&1
          comp_ret=$?
          echo "# NOTE: compile exited with $comp_ret" >>$scan_log
          [ $comp_ret -ne 0 ] && echo "$pre_dir/$file" >>$scan_failed
          ;;
        esac
      done
    fi
  done
}

# -----------------------------------------------------
# Handle compile all jar files to objects
# -----------------------------------------------------
handle_jarfiles() {
  # Performance Anchor
  echo "NEW_JAVA_HANDLE_JARFILES|$(date +%s)" >>$performance_log
  # Traverse through all targets to compile all of them to object-files.
  for target in $targets; do
    compile_only="true"
    init ${target}
    pre_dir="${preprocess_files}/${target}/jarfiles"
    comp_option=${scan_java_jfe_option}
    # This ${pre_dir} should exist, otherwise we may face some issues in the targets list.
    if [ -d "${pre_dir}" ]; then
      # The directory contains at least two files:
      # xxxxx.preprocess/${target}.dir/xcalibyte.properties
      # xxxxx.preprocess/${target}.dir/jarfiles/xxxxx.jar
      if [ ${compile_only} = "false" ]; then

        echo "===========================================================================" >> $scan_log
        echo "### handle jarfiles directory for ${target}, in pwd = $(pwd) ......   "      | tee -a $scan_log
        echo "TIME: $(date) | TIMESTAMP: $(date +%s) "                                     | tee -a $scan_log

        # this is a module target (user application)
        # find all the dependencies and add as the classpaths($cps)
        cps=
        dependencies=
        # Adding the project itself onto the classpath
        append_jar ${preprocess_files}/${target}/jarfiles
        get_deps ${target}
        echo "## after get_deps, the dependencies are ${dependencies}"                     >>$scan_log
        if [ -n "${dependencies}" ]; then
          for one_dependency in ${dependencies}; do
            # Add as -Wf,-cp=....../....../xxx.jar
            append_jar ${preprocess_files}/${one_dependency}.dir/jarfiles
          done
        fi
        echo "[dependencies of ${target}] ${dependencies}"                                 >>$dep_log
        echo "[classpaths of ${target}] $cps"                                              >>$dep_log
        echo "===========================================================================" >>$scan_log
      else
        # This means it is a dependency library target(also used as v-table only library target), no need to compile it to get the v-table now.
        comp_option="${comp_option} ${scan_java_jfe_vtable_option}"
        if [ ! -z ${scan_java_skip_vtable} ] && [ ${scan_java_skip_vtable} = "YES" ]; then
          # Skip all vtable generation
          echo "### skip handle jarfiles directory for ${target}, in pwd = $(pwd) ......   "      | tee -a $scan_log
          continue;
        fi
      fi

      # Use the fileinfo.json information provided and search for source code inside.
      if [ -f "${preprocess_files}/../fileinfo.json" ]; then
        comp_option="${comp_option} -Wf,-srcPathInput=${preprocess_files}/../fileinfo.json "
      fi

      # Should be one jar at one dir,
      # but we put this here in case we have more
      OLDIFS=$IFS # Change the IFS
      IFS=$'\n'
      fileArray=($(find "${pre_dir}" -name '*.jar'))
      IFS=$OLDIFS           # restore it
      tLen=${#fileArray[@]} # Read the array length
      for ((i = 0; i < ${tLen}; i++)); do
        file="${fileArray[$i]}"
        # Change suffix .jar into .o
        without_ext_name=${file%.*}
        echo "### handle one file: $file ......"                            | tee -a $scan_log
        obj_options="-o ${without_ext_name}.o -c"
        # Performance Anchor
        echo "NEW_JAVA_HANDLE_ONE_JAR|${file}|$(date +%s)"                  >>$performance_log
        # compile with xvsa, generating a .o file for the target
        echo "# command: xvsa $common_scan_options $comp_option $obj_options ${file} ${cps}"     >>$scan_log
        xvsa $common_scan_options $comp_option $obj_options ${file} ${cps}                       >>$scan_log 2>&1
        scan_ret=$?
        echo "NEW_JAVA_HANDLE_ONE_JAR_END|${file}|$(date +%s)"              >>$performance_log
        echo "# NOTE: xvsa exited with $scan_ret" >>$scan_log
        if [ $scan_ret -ne 0 ]; then
          echo "[CMD] XVSA result is not zero, quitting...."                >>$scan_log
          echo "${preprocess_files}/${target}" >>$scan_failed
          exit $((20 + $scan_ret)) # We quit immediately...
        fi
      done
    fi
  done
  echo "NEW_JAVA_HANDLE_JARFILES_END|$(date +%s)"                           >>$performance_log
}

# --------------------------------------------------------
# Scan all the object files compiled by handle_jarfiles
# --------------------------------------------------------
new_java_xfa_scan() {
  echo "NEW_JAVA_XVSA_SCAN|$(date +%s)"                                     >>$performance_log
  for target in $targets; do

    # We only scan those modules, not libraries
    compile_only="true"
    init $target
    pre_dir="${preprocess_files}/$target/jarfiles"

    # The directory should look like, containing the three:
    # xxxxx.preprocess/${target}/xcalibyte.properties
    # xxxxx.preprocess/${target}/jarfiles/xxx.jar
    # xxxxx.preprocess/${target}/jarfiles/xxx.o

    # Check if this is a application module directory by searching for 'compile_only=false'
    if [ -d "$pre_dir" ] && [[ ${compile_only} = "false" ]] ; then
      echo "==========================================================================="      >> $scan_log
      echo "### handle jarfiles directory for ${target}, in pwd = $(pwd) ...... $(date)"| tee -a $scan_log

# no need any more, since now only need to cross scan user project .o and rt.o(or maybe udr library)
:<<!
      # find all the dependencies and add as the vtables list
      vtables=
      dependencies=
      get_deps ${target}
      echo "## after get_deps, the dependencies are ${dependencies}"                          >> $scan_log
      if [ -n "$dependencies" ]; then
        for one_dependency in $dependencies
        do
          # Add this file directly to the vtables variable
          append_vtable ${preprocess_files}/${one_dependency}.dir/jarfiles;
        done
      fi
      echo "[dependencies of ${target}] ${dependencies}"                                      >> $dep_log
      echo "[vtables of ${target}] ${vtables}"                                                >> $dep_log
      echo "==========================================================================="      >> $scan_log
!

      # Changing the IFS for reading contents with line separators.
      OLDIFS=$IFS # Change the IFS
      IFS=$'\n'
      fileArray=($(find "${pre_dir}" -name '*.[oB]'))
      IFS=$OLDIFS # restore it
      tLen=${#fileArray[@]}
      for (( i=0; i<${tLen}; i++ ));
      do
        one_file="${fileArray[$i]}"
        echo "### handle one module: ${one_file} ......"                            | tee -a $scan_log

         # Cross scan targets
        echo "### processing file [$one_file], cross scan $targs ......"            | tee -a $scan_log

        # Use java option
        option=${scan_java_option}

        # Prepare the scan directory
        scan_dir="${scan_result}"
        mkdir -p ${scan_dir}

        ## Entering the scan_dir to perform xvsa there:
        echo "[CMD] cd ${scan_dir}"                                                       >> $scan_log
        cd ${scan_dir}

        if [ -f xvsa-xfa-dummy.v ]; then
          # Rename previously existing v file
          mv xvsa-xfa-dummy.v "xvsa-xfa-dummy-${v_counter}.v"
        fi

        if [ -f xvsa-xfa-dummy.vtxt ]; then
          # Rename previously existing vtxt file
          mv xvsa-xfa-dummy.vtxt "xvsa-xfa-dummy-${v_counter}.vtxt"
        fi

        # Performance Anchor
        echo "NEW_JAVA_XVSA_SCAN_MODULE|${one_file}|$(date +%s)" >> $performance_log

        ## Invoking XVSA, with common-objects (rt.o), and other library v-tables (see above)
        echo "[CMD] xvsa ${common_scan_options} ${option} ${one_file} ${extra_common_objects} " >>$scan_log 2>&1
        module_scan_start "${one_file}"
        xvsa ${common_scan_options} ${order_options} ${option} ${one_file} ${extra_common_objects} >>$scan_log 2>&1
        scan_ret=$?
        module_scan_end "${one_file}"
        echo "# NOTE: scan exited with ${scan_ret}"                                          >> $scan_log
        echo "NEW_JAVA_XVSA_SCAN_MODULE_END|${one_file}|$(date +%s)" >> $performance_log
        v_counter=$((v_counter + 1))
        if [ $scan_ret -ne 0 ]; then
          echo "[CMD] XVSA result is not zero, removing v files...."                       >> $scan_log
          echo "${preprocess_files}/${target}"                                             >> $scan_failed
          # remove uncompleted .v .vtxt files
          rm -vf $scan_dir/*.v $scan_dir/*.vtxt                                            >> $scan_log 2>&1
          exit $((20 + scan_ret));
        fi
      done
    fi
  done
  echo "NEW_JAVA_XVSA_SCAN_END|$(date +%s)" >> $performance_log
}

## Append -Wf,-cp=jarfile to the 'cps' variable
append_jar() {
  obj_dir=$1
  if [ -d "$obj_dir" ]; then
    num=$(ls $obj_dir/*.jar 2>/dev/null |wc -l)
    if [ $num -ne 0 ]; then
      cps="-Wf,-cp=$(ls $obj_dir/*.jar) $cps"
    fi
  fi
}

## Append object files to the 'vtables' variable
append_vtable() {
  obj_dir=$1
  if [ -d "$obj_dir" ]; then
    num=$(ls $obj_dir/*.jar 2>/dev/null |wc -l)
    if [ $num -ne 0 ]; then
      vtables="$(ls $obj_dir/*.[oB]) $vtables"
    fi
  fi
}

## Append object file to the 'objs' variable
append_obj() {
  obj_dir=$1
  if [ -d "$obj_dir" ]; then
    num=$(ls $obj_dir/*.[o,O] 2>/dev/null |wc -l)
    if [ $num -ne 0 ]; then
      objs="$(ls $obj_dir/*.[o,O]) $objs"
    fi
  fi
}

get_deps(){
  local dep_target=$1
  local dep_targs
  has_dep=0
  if [ -f "${preprocess_files}/$dep_target/xcalibyte.properties" ]; then
    while read -r line
    do
      case "$line" in
        dependencies=*)
          dep=$(echo $line | awk -F= '{print $2}' | sed 's/\"//g')
          dependencies="$dep $dependencies"
          has_dep=1
          ;;
      esac
    done < ${preprocess_files}/${dep_target}/xcalibyte.properties
    # We do not search for transient dependencies since we don't have any
    # if [ $has_dep -eq 1 ]; then
    #   for dep_targs in $dep
    #   do
    #     get_deps $dep_targs
    #   done
    # fi
  fi
}

# scan every single object file, generate one v file at a time
non_cross_scan() {
  init
  if [ -n "$c_scan_options" ]; then
    option=$c_scan_options
  else
    option=$cxx_scan_options
  fi

  v_counter=0
  number_of_failed=0
  scan_dir="$scan_result"
  mkdir -p $scan_dir
  cd $scan_dir

  objs=$(find ${preprocess_files} -name "*.o" -type f)
  if [ -n "$objs" ]; then
    echo "### non cross scan ${objs} ......" | tee -a $scan_log
    for obj in $objs; do
      if [ -f xvsa-xfa-dummy.v ]; then
        # Rename previously existing v file
        mv xvsa-xfa-dummy.v "xvsa-xfa-dummy-${v_counter}.v"
      fi

      if [ -f xvsa-xfa-dummy.vtxt ]; then
        # Rename previously existing vtxt file
        mv xvsa-xfa-dummy.vtxt "xvsa-xfa-dummy-${v_counter}.vtxt"
      fi

      echo "# command: xvsa $common_scan_options $scan_c_ext_option $option $obj ${extra_common_objects}" >>$scan_log
      xvsa $common_scan_options $order_options $scan_c_ext_option $option $obj ${extra_common_objects} >>$scan_log 2>&1
      scan_ret=$?
      echo "# NOTE: scan $obj exited with $scan_ret" >>$scan_log
      if [ $scan_ret -ne 0 ]; then
        [ $number_of_failed -eq 0 ] && echo "below are non cross scan failed case:" >> $scan_failed
        echo "$pre_dir/$file" >> $scan_failed
        # remove uncompleted .v .vtxt files
        [ -f xvsa-xfa-dummy.v ] && rm -vf $scan_dir/xvsa-xfa-dummy.v >>$scan_log 2>&1
        [ -f xvsa-xfa-dummy.vtxt ] && rm -vf $scan_dir/xvsa-xfa-dummy.vtxt >>$scan_log 2>&1
        number_of_failed=$((number_of_failed + 1))
      fi

      v_counter=$((v_counter + 1))
    done
  else
    echo "${preprocess_files}" >>$scan_failed
    echo "### ignore scan, since no object files found" | tee -a $scan_log
  fi
}

# cross file scan.
cross_file_scan() {
# no need anymore
:<<!
  if [ ${scan_cross_file} -eq 0 ]; then
    for target in $targets; do
      file=$(find ${preprocess_files}/${target} -name '*.v')
      if [ -n "${file}" ]; then
        mkdir -p ${scan_result}/${target}
        cp -vf ${file} ${scan_result}/${target}                                          >> $scan_log
      fi
    done
    return 0
  fi

  for targs in $targets
  do
    init $targs
    objs=
    dependencies=
    append_obj ${preprocess_files}/$targs/preprocess
    append_obj ${preprocess_files}/$targs/objfiles
    get_deps $targs
    if [ -n "$dependencies" ]; then
      for my_targs in $dependencies
      do
        append_obj ${preprocess_files}/$my_targs/preprocess
        append_obj ${preprocess_files}/$my_targs/objfiles
      done
    fi
    echo "[dependencies of $targs] $dependencies"                                        >> $dep_log
    echo "==========================================================================="   >> $scan_log
    if [ "${targs##*.}" = "a" -o "${targs##*.}" = "so" ]; then
      if [ "$compile_only" = "false" ]; then
        echo "### skip scan $targs separately ......" | tee -a $scan_log
        continue
      fi
    fi
!
  init
  objs=$(find ${preprocess_files} -name "*.o" -type f)
  if [ -n "$objs" ]; then
    echo "### cross scan ${objs} ......" | tee -a $scan_log
    if [ -n "$c_scan_options" ]; then
      option=$c_scan_options
    else
      option=$cxx_scan_options
    fi

    scan_input_param=$objs
    arg_max=$(getconf ARG_MAX)
    objs_len=${#objs}
    echo "# system arg max limit: $arg_max, scan params actual length: $objs_len" >>$scan_log
    if [ $objs_len -gt $arg_max ]; then
      echo $objs > $(pwd)/$objects_file_name
      scan_input_param="@"$(pwd)/$objects_file_name
      echo "# scan_input_param: $scan_input_param" >>$scan_log
    fi

    echo "# command: xvsa $common_scan_options $scan_c_ext_option $option $scan_input_param ${extra_common_objects}" >>$scan_log
    scan_dir="$scan_result"
    mkdir -p $scan_dir
    cd $scan_dir
    module_scan_start "$scan_input_param"
    xvsa $common_scan_options $order_options $scan_c_ext_option $option $scan_input_param ${extra_common_objects} >>$scan_log 2>&1
    scan_ret=$?
    module_scan_end "$scan_input_param"
    echo "# NOTE: scan exited with $scan_ret" >>$scan_log
    if [ $scan_ret -ne 0 ]; then
      echo "${preprocess_files}" >>$scan_failed
      # remove uncompleted .v .vtxt files
      rm -vf $scan_dir/*.v $scan_dir/*.vtxt >>$scan_log 2>&1
    fi
  else
    echo "${preprocess_files}" >>$scan_failed
    echo "### ignore scan, since no object files found" | tee -a $scan_log
  fi
:<<!
    cd $cur_dir
  done
!
}

# -------------------------------------------------------------------
# Way of performing java scans when JFE is run on agent side,
# @Deprecated
# -------------------------------------------------------------------
java_xfa_scan() {
  init java.scan;
  # Search for .o or .B files (both working for now)
  objs=$(find ${preprocess_files} -name "*.[oB]")
  v_counter=0

  if [ -n "$objs" ]; then
    # FIXME: Replace iterating over the string to globbing
    # TODO:   see https://github.com/koalaman/shellcheck/wiki/SC2045
    for one_file in $objs; do
      # Cross scan targets
      echo "### processing file [$one_file], cross scan ......"                  | tee -a $scan_log

      # Use java option
      option=$scan_java_option
      # Prepare the scan directory
      scan_dir="$scan_result/"
      mkdir -p $scan_dir

      ## Entering the scan_dir to perform xvsa there:
      echo "[CMD] cd $scan_dir"                                                         >> $scan_log
      cd $scan_dir

      if [ -f xvsa-xfa-dummy.v ]; then
        # Rename previously existing v file
        mv xvsa-xfa-dummy.v "xvsa-xfa-dummy-${v_counter}.v"
      fi
      if [ -f xvsa-xfa-dummy.vtxt ]; then
        # Rename previously existing vtxt file
        mv xvsa-xfa-dummy.vtxt "xvsa-xfa-dummy-${v_counter}.vtxt"
      fi
      echo "# command: xvsa $common_scan_options $option $one_file $extra_common_objects " >>$scan_log
      ## Invoking XVSA
      module_scan_start "$one_file"
      xvsa $common_scan_options $order_options $option $one_file $extra_common_objects &>>$scan_log
      scan_ret=$?
      module_scan_end "$one_file"
      echo "# NOTE: scan exited with $scan_ret" >>$scan_log
      v_counter=$((v_counter + 1))
      if [ $scan_ret -ne 0 ]; then
        echo "[CMD] XVSA result is not zero, removing v files...."                       >> $scan_log
        echo "$one_file"                                                                 >> $scan_failed
        # remove uncompleted .v .vtxt files
        rm -vf $scan_dir/*.v $scan_dir/*.vtxt                                            >> $scan_log 2>&1
        return $scan_ret
      fi
    done
  else
    echo "${preprocess_files}"                                                           >> $scan_failed
    echo "### ignore scan, since no object files found"                            | tee -a $scan_log
  fi
}

# -------------------------------------------------------------------
# Compiling the rt.jar and other related Jar files.
# -------------------------------------------------------------------
handle_extra_objects() {
  echo "HANDLE_RT_LIBRARY|$(date +%s)" >>$performance_log
  # Use the work_base_dir to find the realpath of work_base_dir
  work_base_dir=$(dirname ${preprocess_files})
  work_base_dir=$(realpath $work_base_dir)
  if [ -d $work_base_dir/extra-object ]; then
    if [ -d ${work_base_dir}/extra-object/jdk.dir ]; then
      if [ ! -f ${work_base_dir}/extra-object/jdk.dir/jarfiles/rt.o ] &&
        [ -f ${work_base_dir}/extra-object/jdk.dir/jarfiles/rt.jar ]; then
        # We first need to compile or use the rt.o file
        echo "Found the runtime.jar up for compilation, "                              | tee -a $scan_log
        echo "trying to compile ${work_base_dir}/extra-object/jdk.dir/jarfiles/rt.jar" | tee -a $scan_log
        comp_option=${scan_java_jfe_option}
        comp_option="${comp_option} ${scan_java_jfe_vtable_option}"
        obj_options="-o $work_base_dir/extra-object/jdk.dir/jarfiles/rt.o -c"
        files=${work_base_dir}/extra-object/jdk.dir/jarfiles/rt.jar
        # Add related Jarfiles to the 'cps' variable.
        append_jar ${preprocess_files}/jdk.dir/jarfiles
        echo "# command: xvsa $common_scan_options $comp_option $obj_options ${files} ${cps}"            >>$scan_log
        xvsa ${common_scan_options} ${comp_option} ${obj_options} ${files} ${cps}                          >>$scan_log 2>&1;
        scan_ret=$?
        echo "# NOTE: xvsa exited with $scan_ret" | tee -a $scan_log
        if [ $scan_ret -ne 0 ]; then
          echo "${work_base_dir}/extra-object/jdk.dir/jarfiles/rt.jar" >>$scan_failed
        fi
      elif [ -f ${work_base_dir}/extra-object/jdk.dir/jarfiles/rt.o ]; then
        echo "# Found existing runtime v-table under ${work_base_dir}/extra-object/jdk.dir/jarfiles/rt.o"
      else
        echo "# WARN: Found none of the valid jdk.dir existing, continuing with caution"
      fi
    fi
    echo "HANDLE_RT_LIBRARY_END|$(date +%s)" >>$performance_log

    # Here, we add all the existing .o and perhaps the generated file above to the list
    # 'extra_common_objects'
    local existing_objs
    existing_objs=$(find $work_base_dir/extra-object -name "*.[oB]")
    for one_file in ${existing_objs}; do
      echo "# Found one extra-object: ${one_file}"
      extra_common_objects="$extra_common_objects ${one_file}"
    done
    handle_extra_objects_common
    echo "# Finalized extra_common_objects = $extra_common_objects" | tee -a $scan_log
  else
    extra_common_objects=""
    echo "# No extra-object dir was found, extra_common_objects = '' " | tee -a $scan_log
  fi
}

# -------------------------------------------------------------------
#  Handle the user defined rules in extra-object folder
#  this is used for debug purpose at the moment,
#  dealing with uploaded udr files from agent side.
# -------------------------------------------------------------------
handle_extra_objects_common() {
  # Use the work_base_dir to find the realpath of work_base_dir
  work_base_dir=$(dirname ${preprocess_files})
  work_base_dir=$(realpath $work_base_dir)
  # Finding user_defined_rule from
  # /share/scan/<sid>/extra-object
  # or /share/scan/<sid>/<sid>.preprocess/extra-object
  user_defined_rules=$(find $work_base_dir/extra-object -name "*.udr");
  for one_file in ${user_defined_rules};
  do
    echo "# Found one user defined rule: ${one_file}"                | tee -a $scan_log;
    extra_common_objects="$extra_common_objects ${one_file}"
  done
  user_defined_rules=$(find $preprocess_files/extra-object -name "*.udr");
  for one_file in ${user_defined_rules};
  do
    echo "# Found one in-preprocess user defined rule: ${one_file}"  | tee -a $scan_log;
    extra_common_objects="$extra_common_objects ${one_file}"
  done
}

record_vcs_info() {
  files=$(find $scan_result -name '*.vtxt')
  if [ -z "$files" ]; then
    echo "# no .vtxt files generated, scan may failed, please check $scan_log"
    if [ $scan_ret -ne 0 ]; then
      exit $((20 + $scan_ret))
    fi
    exit 15
  fi
  # remove .v since 2.0.0
  find $scan_result -name '*.v' -exec rm -vf {} \; >>$scan_log
:<<!
  for target in $targets; do
    if [ -d "$scan_result/$target" ]; then
      v_files=$(find $scan_result/$target -name '*.v')
    fi
    if [ -n "$v_files" ]; then
      init $target
!
      v_files=$files
      if [ -n "$vcs_tool" ]; then
        sed -i "s,@@VCSTOOL@@,$vcs_tool,g; s,@@VCSREPO@@,$vcs_repo,g; s,@@VCSVERSION@@,$vcs_version,g" $v_files
      fi
:<<!
    fi
  done
!
}

# ============================================== 
# extract mi files and convert them to udr files
# ==============================================
mi_to_udr() {
  mi_zip="./mi.zip"
  mi_dir="./.mi"
  udr_dir="./.udr"
  convert_log="./.scan_log/convert.log"
  echo "xvsa_path: $xvsa_path"

  # extract mi files
  # cp $mifile_location $mi_gz
  mkdir -p $udr_dir

  # uncompress mi files
  unzip -o $mi_zip -d $mi_dir

  # convert mi files to udr files 
  converter="./rule-builder/scripts/rulebuild.py"
  lang="c"

  # record convert options
  echo "# =========== MI_TO_UDR ===========" > $convert_log
  echo "converter: $converter" >> $convert_log
  echo "lang: $lang" >> $convert_log

  if [ "$(ls -A $mi_dir)" != "" ]; then
    # TODO convert mi files to udr files 
    mifiles=$(find $mi_dir -name "*?.mi")
    # echo "files $mifiles"
    for file in ${mifiles}; do
      echo "converting $file..."
      cmd="$converter $lang $file -o $udr_dir --xvsa_home $xvsa_path"
      echo $cmd >> $convert_log
      $converter $lang $file -o $udr_dir --xvsa_home $xvsa_path 2&>1 >> $convert_log
    done
  fi

  echo "Convert mi files to udr files done";
}

# ===================================================================================================
#trap 'rm -rf $scan_result' EXIT
#check xvsa
if [ ! $(which xvsa) ]; then
  echo "xvsa not work, please install first!"
  exit 12
fi

#remove scan_result
rm -rf $scan_result

#check targets
targets=$(ls -l ${preprocess_files} | awk '/^d/{print$NF}')
if [ -z "$targets" ]; then
  echo "No target found in $1, please check!"
  exit 13
else
  if [ "$targets" = "has_no_target" ]; then
    echo "has_no_target exist."
    scan_cross_file=0
  fi
fi

if [ -n "$scan_token" ]; then
  order_options="$order_options -VSA:token=$scan_token"
fi
if [ -n "$scan_server" ]; then
  order_options="$order_options -VSA:server=$scan_server"
fi

# open file number limit is 1024 on Ubuntu 16.04 system by default, change this limit to max permitted value
max_value=$(ulimit -n -H)
echo "# change open file number limit to $max_value" >>$scan_log
ulimit -n $max_value

echo "----------------------------------"
echo "Performing scanning in xvsa_scan $(date)"
echo "----------------------------------"
xvsa -vvv

# genereate UDR files from MI files
mi_to_udr

if [[ ${scan_mode} == "new_java_scan" ]]; then
  echo "Starting new java xfa scan .... $(date)"
  # Pre-cross file scan
  prescan_start
  handle_extra_objects
  handle_jarfiles
  prescan_end

  # Cross file scan
  scan_start
  new_java_xfa_scan
  scan_end
elif [[ ${scan_mode} == "java_scan" ]]; then
  echo "Starting Java XFA scan  .... $(date)"
  # Pre-cross file scan
  prescan_start
  handle_extra_objects
  prescan_end

  # Cross file scan
  scan_start
  java_xfa_scan
  scan_end
else
  echo "Starting C/C++ scan .... $(date)"
  # Pre scan
  prescan_start
  handle_extra_objects_common
  handle_preprocess_file
  prescan_end

  # scan
  scan_start
  if [ $scan_cross_file -eq 1 ]; then
    cross_file_scan
  else
    non_cross_scan
  fi
  scan_end
fi
record_vcs_info

tar -zcPf $cur_dir/scan_result.tar.gz $scan_result
ret=$?
if [ $ret -ne 0 ]; then
  echo "tar package failed!"
  exit 16
fi

echo "Please check scan log from $scan_log"
echo "Please check scan result at file://$cur_dir/scan_result.tar.gz"
