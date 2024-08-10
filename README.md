In MacOS, if you get an error like this:

`
clang: error: unsupported option '-fopenmp'
`

Then you need to install `libomp` with `brew install llvm libomp`
And export the following environment variables:

```bash
export CXX=g++-13
export CC=gcc-13
```

Then you can run the script with `python3 find_duplicate_images.py`
