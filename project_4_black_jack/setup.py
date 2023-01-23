from distutils.core import setup
import py2exe

py2exe.freeze(console=["black_jack.py"])
