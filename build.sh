docker rmi agenticdb
docker builder prune --all --force
docker build --no-cache -t agenticdb .

