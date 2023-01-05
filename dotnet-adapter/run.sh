pushd DotnetPreAdapter >/dev/null 
from_dir=$1
out_dir=$2
shift
shift
dotnet run --from_dir $from_dir --out_dir $out_dir $@
popd >/dev/null 
