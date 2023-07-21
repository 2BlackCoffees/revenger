pushd DotnetPreAdapter >/dev/null
from_dir=$1
out_dir=$2
shift
shift
cygpath -h > /dev/null 2>&1
if [[ $? == 0 ]]; then
    from_dir=$(cygpath -w $from_dir)
    out_dir=$(cygpath -w $out_dir)
fi
dotnet run --from_dir $from_dir --out_dir $out_dir $@
popd >/dev/null
