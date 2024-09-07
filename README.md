# Image Duplicate Finder Project

## Overview

This project focuses on rapidly identifying duplicate images within a dataset. The motivation behind this project is to optimize storage usage and eliminate redundant images, which can be critical for maintaining large image repositories or organizing personal photo collections.

## Features

Detects and removes duplicate images efficiently.

Command-line interface for ease of automation.

Desktop UI for user-friendly interaction.

## Usage for Common Users

To find and eliminate duplicate images in a directory, you can use the script as follows:

`python find_duplicate_images.py --dir <path_to_directory>`

For more help on usage:

`python -m find_duplicate_images -h`

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

`python3 -m find_duplicate_images`

## Building the Desktop UI

To build the desktop UI, use pyinstaller with the provided spec file:

`pyinstaller ./snap_sweep.spec --noconfirm`
