#!/bin/bash

# Configuration
REPO="nullvoider07/macos_actuation_control"
BINARY_NAME="macos-actuation"

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS_TYPE="linux";;
    Darwin*)    OS_TYPE="osx";;
    *)          echo "Unsupported OS: ${OS}"; exit 1;;
esac

# Detect Architecture
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64)    ARCH_TYPE="x64";;
    arm64)     ARCH_TYPE="arm64";;
    aarch64)   ARCH_TYPE="x64";;
    *)         echo "Unsupported Architecture: ${ARCH}"; exit 1;;
esac

echo "Detected: ${OS_TYPE} (${ARCH_TYPE})"

# Get Latest Release Tag from GitHub API
echo "Fetching latest version..."
LATEST_TAG=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_TAG" ]; then
    echo "Error: Could not find latest release."
    exit 1
fi

# Extract Version Number (Remove 'mac-v' prefix)
VERSION=${LATEST_TAG#mac-v}
echo "Latest Version: ${VERSION}"

# Construct Download URL
# Matches the naming convention from your YAML: macos-actuation-{VERSION}-{OS}-{ARCH}.tar.gz
FILE_NAME="macos-actuation-${VERSION}-${OS_TYPE}-${ARCH_TYPE}.tar.gz"
DOWNLOAD_URL="https://github.com/$REPO/releases/download/$LATEST_TAG/$FILE_NAME"

# Download
echo "Downloading $DOWNLOAD_URL..."
curl -L -o "$FILE_NAME" "$DOWNLOAD_URL"

if [ $? -ne 0 ]; then
    echo "Download failed. Please check your network or if the asset exists."
    exit 1
fi

# Install
echo "Installing..."
tar -xzf "$FILE_NAME"
chmod +x "$BINARY_NAME"

# Move to /usr/local/bin (requires sudo)
echo "Moving binary to /usr/local/bin (requires sudo)..."
if sudo mv "$BINARY_NAME" /usr/local/bin/$BINARY_NAME; then
    echo "✅ Installation complete! You can now run '$BINARY_NAME' from anywhere."
else
    echo "❌ Failed to move binary. It is located in the current directory."
fi

# Cleanup
rm "$FILE_NAME"