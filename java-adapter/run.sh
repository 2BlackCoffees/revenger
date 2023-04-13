from_dir=$1
out_dir=$2
shift
shift
mvn install && mvn exec:java -Dexec.args="--from_dir $from_dir --out_dir $out_dir $*"
