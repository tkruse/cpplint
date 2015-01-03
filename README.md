# cpplint - static code checker for C++

[![Build Status](https://travis-ci.org/tkruse/cpplint.svg)](https://travis-ci.org/tkruse/cpplint)

This project provides cpplint as a pypi package
(https://pypi.python.org/pypi/cpplint). It follows the code maintained as SVN
repository by google employees at
http://google-styleguide.googlecode.com/svn/trunk/cpplint.


It is possible that this repo lags behind the SVN repo, if you notice this,
feel free to open an issue asking for an update. The git-svn branch should 
be a 1-to-1 copy of the history in SVN.

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

- project folder structure slightly changed for easier packaging
- more default extensions
- python 3k compatibility
- minor fixes around default file extensions
- continuous integration on travis

## Maintaining

Prerequisites: Install git-svn.
To fetch the latest changes from SVN upstream after cloning:

```
git svn init http://google-styleguide.googlecode.com/svn/trunk/cpplint/
git svn fetch
git checkout git-svn/git-svn -b git-svn
git svn fetch
```

- Then re-apply all custom commits or do a merge in another way (this is messy).
- Version Bump, update changelog
- Create new release in pypi
