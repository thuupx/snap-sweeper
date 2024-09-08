# Snap Sweep - Image Duplicate Finder

## Overview

Snap Sweep - The Image Duplicate Finder aims to provide a robust solution for identifying and managing duplicate images within large datasets. By detecting redundant images, Snap Sweep helps optimize storage usage and streamline image organization, which is essential for both professional and personal use cases.

Leveraging advanced image processing techniques, the tool offers a command-line interface for automation and a desktop UI for ease of use, supporting almost all image formats.

### Key Objectives

- **Storage Optimization**: Free up storage by removing unnecessary duplicates.
- **Efficient Management**: Simplify the organization of large collections of images.
- **User-Friendly Interface**: Provide both command-line and desktop UI options for flexible usage.
- **Support for Multiple Formats**: Ensure broad compatibility with different image formats.
- **Zero External Requests**: The tool does not make any external requests, your images are not sent anywhere.

## Features

- Detects and removes duplicate images efficiently.
- Command-line interface for ease of automation.
- Desktop UI for a user-friendly interface.
- Supports almost all image formats.
- Optimized for large image datasets.
- Automatically identifies and moves duplicate images to a designated sub-folder.

## Usage for Common Users

To find and eliminate duplicate images in a directory, you can use the script as follows:

`python -m snap_sweep_cli.py --dir <path_to_directory>`

For more help on usage:

`python -m snap_sweep_cli -h`

You can also use the desktop UI to find and eliminate duplicate images with easy to understand interface.

## Developer Setup

### Prerequisites

Ensure you have the necessary build tools and libraries installed.

For macOS:

If you encounter the following error:

`clang: error: unsupported option '-fopenmp'`

Install the required libraries:

`brew install llvm libomp`

Additionally, ensure g++-14 and gcc-14 are installed:

```bash
which g++-14
which gcc-14
```

If not, install them with:

`brew install gcc@14`

Then set the environment variables:

```bash
export CXX=g++-14
export CC=gcc-14
```

If you cannot find gcc, locate it with:

`which gcc`

### Dependencies

Install the required Python packages:

`pip install -r requirements.txt`

## Running the Script

To execute the duplicate image finder script:

`python3 -m snap_sweep_cli`

## Building the Desktop UI

To build the desktop UI, use pyinstaller with the provided spec file:

`pyinstaller ./snap_sweep.spec --noconfirm`
