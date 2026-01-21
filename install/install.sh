#!/bin/bash

# Configuration
REPO="nullvoider07/macos_actuation_control"
BINARY_NAME="macos-actuation"
INSTALL_DIR="$HOME/.local/bin"

if command -v "$BINARY_NAME" &> /dev/null; then
    echo "⚠️  macos-actuation is already installed."
    echo "💡 To update to the latest version, simply run:"
    echo "   $BINARY_NAME update"
    echo ""
    read -p "Do you still want to force a reinstall? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo "Proceeding with reinstall..."
fi

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

VERSION=${LATEST_TAG#mac-v} 
echo "Latest Version: ${VERSION}"

# Construct Download URL
FILE_NAME="macos-actuation-${VERSION}-${OS_TYPE}-${ARCH_TYPE}.tar.gz"
DOWNLOAD_URL="https://github.com/$REPO/releases/download/$LATEST_TAG/$FILE_NAME"

# Download
echo "Downloading $DOWNLOAD_URL..."
curl -L -o "$FILE_NAME" "$DOWNLOAD_URL"

if [ $? -ne 0 ]; then
    echo "Download failed. Please check your network or if the asset exists."
    exit 1
fi

# Install to ~/.local/bin
echo "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
tar -xzf "$FILE_NAME"
mv "$BINARY_NAME" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$BINARY_NAME"

# macOS Specific: Remove Quarantine Attribute
if [[ "$OS_TYPE" == "osx" ]]; then
    echo "Removing macOS quarantine attribute..."
    xattr -d com.apple.quarantine "$INSTALL_DIR/$BINARY_NAME" 2>/dev/null || true
fi

# Clean up
rm "$FILE_NAME"

# Update PATH if needed
SHELL_CONFIG=""
case "$SHELL" in
    */zsh) SHELL_CONFIG="$HOME/.zshrc" ;;
    */bash) SHELL_CONFIG="$HOME/.bashrc" ;;
    *) SHELL_CONFIG="$HOME/.profile" ;;
esac

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "Adding $INSTALL_DIR to PATH in $SHELL_CONFIG..."
    echo "" >> "$SHELL_CONFIG"
    echo "# macOS Actuation Control CLI" >> "$SHELL_CONFIG"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"
    
    echo "✅ Installation complete!"
    echo "⚠️  Please run the following command to apply changes:"
    echo "   source $SHELL_CONFIG"
else
    echo "✅ Installation complete! (PATH is already configured)"
fi