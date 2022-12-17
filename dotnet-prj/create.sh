dotnet new sln
dotnet new console -o DotnetPreAdapter
cp ../docker/dotnet/* DotnetPreAdapter
dotnet sln add DotnetPreAdapter
cd DotnetPreAdapter
dotnet build
