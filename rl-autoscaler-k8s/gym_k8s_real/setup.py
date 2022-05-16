from setuptools import setup

setup(name='gym_k8s_real',
      version='0.0.1',
      install_requires=['gym','requests','pint','pyyaml']  # And any other dependencies foo needs
      #dependency_links=['http://github.com/kubernetes-client/repo/tarball/master#egg=python-12.0.0-snapshot']
)
