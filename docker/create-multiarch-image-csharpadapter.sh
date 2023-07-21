basepath=$( dirname -- "$( readlink -f -- "$0" )" )
pushd $basepath
cd DotnetPreAdapter
rm -rf *
cd ..
cp -r $basepath/../dotnet-adapter/DotnetPreAdapter/*.cs DotnetPreAdapter
docker buildx create --name mybuilder
docker buildx use mybuilder
docker buildx inspect mybuilder --bootstrap
docker buildx build \
    -f Dockerfile.csharpadapter \
    --platform linux/arm64,linux/amd64 \
    -t 2blackcoffees/revenger_csharpadapter:latest . --push
popd
