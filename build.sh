#!/bin/bash

# Build script for creating architecture-specific builds of Everything by mdfind
# Usage: ./build.sh [arm64|x86_64|both]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [arm64|x86_64|both]"
    echo ""
    echo "Options:"
    echo "  arm64    Build for Apple Silicon Macs (M1, M2, M3)"
    echo "  x86_64   Build for Intel-based Macs"
    echo "  both     Build for both architectures (default)"
    echo ""
}

build_for_arch() {
    local arch=$1
    echo -e "${YELLOW}Building for $arch...${NC}"
    
    # Build with PyInstaller for specific architecture
    pyinstaller --onefile --windowed --noconsole \
        --icon=icon.icns \
        --name="Everything-${arch}" \
        --target-arch=$arch \
        --add-data="LICENSE.md:." \
        --add-data="README.md:." \
        everything.py
    
    # Create archive
    cd dist
    zip -r "../everything-${arch}.zip" "Everything-${arch}"
    cd ..
    
    echo -e "${GREEN}✓ Built Everything-${arch}${NC}"
    echo -e "${GREEN}✓ Created everything-${arch}.zip${NC}"
}

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}Error: PyInstaller is not installed${NC}"
    echo "Please install it with: pip install pyinstaller"
    exit 1
fi

# Check if icon file exists (we'll create a simple one if not)
if [ ! -f "icon.icns" ]; then
    echo -e "${YELLOW}Warning: icon.icns not found. Skipping icon...${NC}"
fi

# Determine what to build
ARCH_TO_BUILD=${1:-both}

case $ARCH_TO_BUILD in
    arm64)
        build_for_arch "arm64"
        ;;
    x86_64)
        build_for_arch "x86_64"
        ;;
    both)
        build_for_arch "arm64"
        build_for_arch "x86_64"
        ;;
    *)
        echo -e "${RED}Error: Invalid architecture specified${NC}"
        print_usage
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Build completed successfully!${NC}"
echo "Built files are in the dist/ directory"
echo "Archives are in the current directory"