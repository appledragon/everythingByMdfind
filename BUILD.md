# Build Process Documentation

This document explains the build process for creating architecture-specific releases of Everything by mdfind.

## Overview

The project now supports building separate releases for different macOS architectures:
- **ARM64**: For Apple Silicon Macs (M1, M2, M3 chips)
- **x86_64**: For Intel-based Macs

## Automated Build (GitHub Actions)

The automated build process is defined in `.github/workflows/Standalone.yaml` and can be triggered manually from the GitHub Actions tab.

### Build Process Steps

1. **Matrix Build**: Builds are created in parallel for both architectures
2. **Dependencies**: Installs Python dependencies and PyInstaller
3. **Icon Generation**: Creates app icon from SVG source
4. **Architecture-Specific Build**: Uses PyInstaller with `--target-arch` flag
5. **Artifact Upload**: Uploads build artifacts for later use
6. **Release Creation**: Creates a GitHub release with both architecture builds

### Workflow Jobs

- `build_and_release`: Creates architecture-specific builds
- `create_and_upload_release`: Creates GitHub release and uploads both builds

## Local Build

### Using the Build Script

The easiest way to build locally is using the provided `build.sh` script:

```bash
# Build for both architectures
./build.sh

# Build for specific architecture
./build.sh arm64    # For Apple Silicon
./build.sh x86_64   # For Intel
```

### Manual Build

For manual builds, use PyInstaller directly:

```bash
# Install PyInstaller
pip install pyinstaller

# Build for specific architecture
pyinstaller --onefile --windowed --noconsole \
  --target-arch=arm64 \
  --name="Everything-arm64" \
  everything.py
```

## Release Artifacts

Each release includes:
- `everything-arm64.zip`: Optimized for Apple Silicon Macs
- `everything-x86_64.zip`: Optimized for Intel-based Macs

## Architecture Detection

Users can determine their Mac's architecture using:

```bash
# Check architecture
uname -m

# Output:
# arm64  -> Use ARM64 build
# x86_64 -> Use x86_64 build
```

## Build Requirements

- macOS (for creating `.app` bundles)
- Python 3.9+
- PyQt6
- PyInstaller
- librsvg (for icon conversion)

## Troubleshooting

### Common Issues

1. **PyInstaller not found**: Install with `pip install pyinstaller`
2. **Icon conversion fails**: Install librsvg with `brew install librsvg`
3. **Architecture mismatch**: Ensure you're using the correct `--target-arch` flag
4. **Missing dependencies**: Run `pip install -r requirements.txt`

### Debug Build

To debug build issues, run PyInstaller with verbose output:

```bash
pyinstaller --onefile --windowed --noconsole \
  --target-arch=arm64 \
  --debug=all \
  everything.py
```

## CI/CD Notes

- Builds run on `macos-latest` GitHub runners
- Uses PyInstaller instead of py2app for better architecture control
- Artifacts are automatically uploaded to GitHub releases
- Build numbers are appended to release tags for uniqueness