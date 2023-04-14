basepath=$( dirname -- "$( readlink -f -- "$0" )" )
pushd $basepath
rm -rf java-adapter
cp -r $basepath/../java-adapter/ java-adapter
docker buildx create --name javabuilder
docker buildx use javabuilder
docker buildx inspect javabuilder --bootstrap
docker buildx build \
  	-f Dockerfile.javaadapter \
    --platform linux/arm64,linux/amd64 \
   	-t 2blackcoffees/revenger_javaadapter:latest . --push
popd