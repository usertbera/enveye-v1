#!/bin/bash
set -e

APP_NAME="enveye-agent"
SRC_FILE="main.go"

echo "🚧 Building $APP_NAME for multiple platforms..."

PLATFORMS=(
  "windows/amd64"
  "linux/amd64"
  "darwin/amd64"
  "darwin/arm64"
)

for PLATFORM in "${PLATFORMS[@]}"
do
    GOOS=${PLATFORM%/*}
    GOARCH=${PLATFORM#*/}

    OUTPUT_DIR="dist/${GOOS}_${GOARCH}"
    OUTPUT_NAME="${APP_NAME}"
    [ "$GOOS" == "windows" ] && OUTPUT_NAME="${APP_NAME}.exe"

    echo "🔨 Building for $GOOS/$GOARCH..."
    mkdir -p "$OUTPUT_DIR"
    GOOS=$GOOS GOARCH=$GOARCH go build -o "${OUTPUT_DIR}/${OUTPUT_NAME}" "$SRC_FILE"
done

echo "✅ All builds completed! Binaries are in the dist/ directory."
