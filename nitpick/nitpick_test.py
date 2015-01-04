#!/usr/bin/python
# -*- coding: utf-8; -*-
# Copyright (c) 2014 The Ostrich | by Itamar O
# pylint: disable=protected-access,too-many-public-methods,too-few-public-methods,bad-indentation,bad-continuation

"""Unit tests for nitpick.py."""

import os
import unittest

import nitpick

def setup_mocks(base_obj, mock_spec):
  """Setup mocking."""
  restore = dict()
  for name, mock in mock_spec.iteritems():
    obj = base_obj
    name_parts = name.split(u'.')
    for name_part in name_parts[:-1]:
      obj = getattr(obj, name_part)
    # save original object for restoring in tearDown
    restore[name] = getattr(obj, name_parts[-1])
    # mock it
    setattr(obj, name_parts[-1], mock)
  return restore

def restore_mocks(base_obj, restore_spec):
  """Restore mocked objects to originals."""
  for name, restore in restore_spec.iteritems():
    obj = base_obj
    name_parts = name.split(u'.')
    for name_part in name_parts[:-1]:
      obj = getattr(obj, name_part)
    # restore it
    setattr(obj, name_parts[-1], restore)

class ProjectOwnershipTest(unittest.TestCase):
  """Test is_project_file function"""

  def setUp(self):
    """Mock os.path.isfile for test."""
    def mock_is_file(file_path):
      """Mock checking for file existence to bypass filesystem."""
      if nitpick._ROOT:
        return os.path.normpath(file_path) in (
            os.path.join(os.path.normpath(nitpick._ROOT), u'foo', u'bar.h'),)
      return os.path.normpath(file_path) in (os.path.join(u'foo', u'bar.h'),)
    def mock_is_dir(dir_path):
      """Mock checking for dir existence to bypass filesystem."""
      if nitpick._ROOT:
        return os.path.normpath(dir_path) in (
            os.path.normpath(os.path.join(nitpick._ROOT, u'foo')),)
      return os.path.normpath(dir_path) in (u'foo',)
    self._mocks = setup_mocks(
      nitpick,
      {
          u'os.path.isfile': mock_is_file,
          u'os.path.isdir': mock_is_dir,
      }
    )

  def tearDown(self):
    """Restore mocked os.path.isfile."""
    restore_mocks(nitpick, self._mocks)
    # Restore mocked root to None
    nitpick._ROOT = None

  def test_simple_check(self):
    """Test that is_project_file behaves as expected for simple cases."""
    self.assertTrue(nitpick.is_project_file(u'foo/bar.h'))
    self.assertTrue(nitpick.is_project_file(u'./foo/bar.h'))
    self.assertFalse(nitpick.is_project_file(u'proj/foo/bar.h'))
    self.assertFalse(nitpick.is_project_file(u'./proj/foo/bar.h'))

  def test_check_with_root(self):
    """Test that is_project_file behaves as expected when root is set."""
    nitpick._ROOT = u'proj'
    self.assertTrue(nitpick.is_project_file(u'foo/bar.h'))
    self.assertTrue(nitpick.is_project_file(u'./foo/bar.h'))
    self.assertFalse(nitpick.is_project_file(u'proj/foo/bar.h'))
    self.assertFalse(nitpick.is_project_file(u'./proj/foo/bar.h'))
    nitpick._ROOT = u'./proj'
    self.assertTrue(nitpick.is_project_file(u'foo/bar.h'))
    self.assertTrue(nitpick.is_project_file(u'./foo/bar.h'))
    self.assertFalse(nitpick.is_project_file(u'proj/foo/bar.h'))
    self.assertFalse(nitpick.is_project_file(u'./proj/foo/bar.h'))

class IncludeSorterTest(unittest.TestCase):
  """Test include-sorter nitpick module"""

  def setUp(self):
    """Mock stuff for tests"""
    def mock_is_proj_file(file_path):
      """Mock testing for project-association to bypass filesystem."""
      base_dir = file_path.split(os.path.sep)[0]
      return base_dir in (u'foo', u'common', u'mymath')
    class MyStdErr(object):
      """Mock STDERR class"""
      def __init__(self):
        """Init empty STDERR mock."""
        self.buffer = list()
      def write(self, message):
        """Write string to mock STDERR."""
        self.buffer.append(message)
    self._stderr = MyStdErr()
    self._mocks = setup_mocks(
      nitpick,
      {
          u'is_project_file': mock_is_proj_file,
          u'sys.stderr': self._stderr,
          u'cpplint._system_wide_external_libs': True,
          u'cpplint._external_lib_prefixes': [u'glog', u'gflags'],
      }
    )

  def tearDown(self):
    """Restore mocked objects to originals."""
    restore_mocks(nitpick, self._mocks)
    # Restore mocked root to None
    nitpick._ROOT = None

  def test_nop_sort(self):
    """Test that already sorted includes returned as it."""
    src_lines = [
      u'#include "foo/bar.h"',
      u'',
      u'#include <stdio.h>',
      u'',
      u'#include <algorithm>',
      u'#include <map>',
      u'#include <vector>',
      u'',
      u'#include "common/logging.h"',
      u'#include "common/util.h"',
      u'#include "mymath/factoiral.h"',
      u'',
    ]
    self.assertListEqual(
      src_lines,
      nitpick.sort_includes('foo/bar.cc', src_lines),
    )

  def test_simple_sort(self):
    """Test that a straight forward sort is performed as expected."""
    src_lines = [
      u'#include "common/util.h"',
      u'#include <vector>',
      u'#include "mymath/factoiral.h"',
      u'#include <map>',
      u'#include <algorithm>',
      u'#include <stdio.h>',
      u'#include "common/logging.h"',
      u'#include "foo/bar.h"',
      u'',
    ]
    exp_lines = [
      u'#include "foo/bar.h"',  # own include
      u'',
      u'#include <stdio.h>',  # C system
      u'',
      u'#include <algorithm>',  # C++ system
      u'#include <map>',
      u'#include <vector>',
      u'',
      u'#include "common/logging.h"',  # Project
      u'#include "common/util.h"',
      u'#include "mymath/factoiral.h"',
      u'',
    ]
    self.assertListEqual(
      exp_lines,
      nitpick.sort_includes('foo/bar.cc', src_lines),
    )

  def test_ext_lib_sort(self):
    """Test that external lib includes are detected and sorted."""
    src_lines = [
      u'#include <gflags/gflags.h>',
      u'#include <vector>',
      u'#include "mymath/factoiral.h"',
      u'#include <map>',
      u'#include <algorithm>',
      u'#include <stdio.h>',
      u'#include <glog/logging.h>',
      u'#include "foo/bar.h"',
      u'',
    ]
    exp_lines = [
      u'#include "foo/bar.h"',  # own include
      u'',
      u'#include <stdio.h>',  # C system
      u'',
      u'#include <algorithm>',  # C++ system
      u'#include <map>',
      u'#include <vector>',
      u'',
      u'#include <gflags/gflags.h>',  # Ext libs
      u'#include <glog/logging.h>',
      u'',
      u'#include "mymath/factoiral.h"',  # Project
      u'',
    ]
    self.assertListEqual(
      exp_lines,
      nitpick.sort_includes('foo/bar.cc', src_lines),
    )

  def test_preserve_poststr(self):
    """Test that the sort preserves post-strings of include lines."""
    src_lines = [
      u'#include <stdio.h>  // old school',
      u'#include\t<\tglog/logging.h\t>\t//for logging, ya know',
      u'#include "foo/bar.h"  // implemented interface',
      u'',
    ]
    exp_lines = [
      u'#include "foo/bar.h"  // implemented interface',  # own include
      u'',
      u'#include <stdio.h>  // old school',  # C system
      u'',
      u'#include <glog/logging.h>\t//for logging, ya know',  # Ext libs
      u'',
    ]
    self.assertListEqual(
      exp_lines,
      nitpick.sort_includes('foo/bar.cc', src_lines),
    )

  def test_surrounding_lines(self):
    """Test that sorter doesn't mess with surrounding lines."""
    src_lines = [
      u'// Copyright message',
      u'// By someone',
      u'#include "common/util.h"',
      u'#include <algorithm>',
      u'#include "mymath/factoiral.h"',
      u'#include "foo/bar.h"',
      u'int main() {',
      u'  return 42;',
      u'}',
      u'',
    ]
    exp_lines = [
      u'// Copyright message',
      u'// By someone',
      u'#include "foo/bar.h"',  # own include
      u'',
      u'#include <algorithm>',  # C++ system
      u'',
      u'#include "common/util.h"',  # Project
      u'#include "mymath/factoiral.h"',
      u'',
      u'int main() {',
      u'  return 42;',
      u'}',
      u'',
    ]
    self.assertListEqual(
      exp_lines,
      nitpick.sort_includes('foo/bar.cc', src_lines),
    )

  def test_with_root_dir(self):
    """Test that sorter understands the root option."""
    nitpick._ROOT = 'proj'
    src_lines = [
      u'#include "common/util.h"',
      u'#include <vector>',
      u'#include "mymath/factoiral.h"',
      u'#include <map>',
      u'#include <algorithm>',
      u'#include <stdio.h>',
      u'#include "common/logging.h"',
      u'#include "foo/bar.h"',
      u'',
    ]
    exp_lines = [
      u'#include "foo/bar.h"',  # own include
      u'',
      u'#include <stdio.h>',  # C system
      u'',
      u'#include <algorithm>',  # C++ system
      u'#include <map>',
      u'#include <vector>',
      u'',
      u'#include "common/logging.h"',  # Project
      u'#include "common/util.h"',
      u'#include "mymath/factoiral.h"',
      u'',
    ]
    self.assertListEqual(
      exp_lines,
      nitpick.sort_includes('proj/foo/bar.cc', src_lines),
    )

  def test_consistent_duplicate(self):
    """Test that sorter detects consistent duplicates, keeps one, and warns."""
    src_lines = [
      u'#include "common/util.h"',
      u'#include <algorithm>',
      u'#include "mymath/factoiral.h"',
      u'#include <algorithm>',
      u'#include "foo/bar.h"',
      u'',
    ]
    exp_lines = [
      u'#include "foo/bar.h"',  # own include
      u'',
      u'#include <algorithm>',  # C++ system
      u'',
      u'#include "common/util.h"',  # Project
      u'#include "mymath/factoiral.h"',
      u'',
    ]
    self.assertListEqual(
      exp_lines,
      nitpick.sort_includes('foo/bar.cc', src_lines),
    )
    self.assertListEqual(
      [u'WARNING: "algorithm" included more than once (consistently) in '
        '"foo/bar.cc:4": #include <algorithm>\n'],
      self._stderr.buffer
    )

  def test_inconsistent_duplicate(self):
    """Test that sorter detects inconsistent duplicates, and breaks."""
    src_lines = [
      u'#include "common/util.h"',
      u'#include <algorithm>  // for std::max',
      u'#include "mymath/factoiral.h"',
      u'#include <algorithm>',
      u'#include "foo/bar.h"',
      u'',
    ]
    with self.assertRaises(RuntimeError):
      nitpick.sort_includes('foo/bar.cc', src_lines)
    self.assertListEqual(
      [u'ERROR: "algorithm" included more than once (inconsistently) in '
        '"foo/bar.cc:4": #include <algorithm>\n'],
      self._stderr.buffer
    )

  def test_wrong_include_style(self):
    """Test that sorter detects wrong include style and warns about it."""
    src_lines = [
      u'#include <common/util.h>',
      u'#include "algorithm"',
      u'#include "mymath/factoiral.h"',
      u'#include "foo/bar.h"',
      u'',
    ]
    exp_lines = [
      u'#include "foo/bar.h"',
      u'',
      u'#include <common/util.h>',
      u'',
      u'#include "algorithm"',
      u'#include "mymath/factoiral.h"',
      u'',
    ]
    self.assertListEqual(
      exp_lines,
      nitpick.sort_includes('foo/bar.cc', src_lines),
    )
    self.assertListEqual(
      [u'WARNING: "common/util.h" looks like a project-file, but is included '
        'with <> in "foo/bar.cc:1": #include <common/util.h>\n',
       u'WARNING: "algorithm" looks like a system-file, but is included with '
        '"" in "foo/bar.cc:2": #include "algorithm"\n'],
      self._stderr.buffer
    )

if __name__ == '__main__':
  unittest.main()
