from_dir=$1
out_dir=$2
shift
shift
cygpath -h > /dev/null 2>&1
if [[ $? == 0 ]]; then
    from_dir=$(cygpath -w $from_dir)
    out_dir=$(cygpath -w $out_dir)
fi
mvn install && mvn exec:java -Dexec.args="--from_dir $from_dir --out_dir $out_dir $*"
