# cpplint - static code checker for C++

[![Build Status](https://travis-ci.org/tkruse/cpplint.svg)](https://travis-ci.org/tkruse/cpplint)

This project provides cpplint as a pypi package
(https://pypi.python.org/pypi/cpplint). It follows the code hosted by google employees at
https://github.com/google/styleguide (was http://google-styleguide.googlecode.com/svn/trunk/cpplint).

The goal is to include contributions to cpplint from various authors, since google currently does not show any interest in modifications to cpplint.

This fork should attempt to remain backwards compatible to the google cpplint fork in the output (except for fixing bugs), and also keep the changes to the codebase minimal to allow easy merges between both codebases.


It is possible that this repo lags behind the google repo, if you notice this, feel free to open an issue asking for an update.

To install from pypi:

```
$ pip install cpplint
```

The run by calling
```
$ cpplint [OPTIONS] files
```

For more info, see [Original README](README)

## Customizations

The modifications in this branch are minor fixes and cosmetic changes:

- more default extensions
- python 3k compatibility
- minor fixes around default file extensions
- continuous integration on travis

## Alternatives

Similar tools:
- [cppcheck](https://github.com/danmar/cppcheck)
- Facebooks [infer](http://fbinfer.com)
- [ClangFormat](http://clang.llvm.org/docs/ClangFormat.html)
