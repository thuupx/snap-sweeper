## Build prerequisites

In MacOS, if you get an error like this:

`
clang: error: unsupported option '-fopenmp'
`

Then you need to install `libomp` with `brew install llvm libomp`
And export the following environment variables:

Confirm g++-14 and gcc-14 are installed with `which g++-14` and `which gcc-14`
If not, install them with `brew install gcc@14`
Then export the following environment variables:

```bash
export CXX=g++-14
export CC=gcc-14
```

Incase gcc not found, you can find it with `which gcc`

Then you can run the script with `python3 find_duplicate_images.py`

### Packages

`pip install -r requirements.txt`

`pyinstaller ./find_duplicates.spec`

### Usage

`python -m find_duplicate_images -h` for help
