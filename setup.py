from setuptools import setup, find_packages
import scuts

setup(name="scuts",
      version=scuts.__version__,
      description='Python Standard Shortcuts',
      author='Arthur RENAUD',
      author_email='arthur.b.renaud@gmail.com',
      url='',
      # packages=['distutils', 'distutils.command'],
      # package_dir={'': 'stdscuts'},
      packages=find_packages(),
      tests_require=["pytest"],
      python_requires='>=3.5',
      setup_requires=["pytest-runner"],
      long_description=open('README.md').read(),

      # Active la prise en compte du fichier MANIFEST.in
      include_package_data=True,
      package_data={'': ['ressources/jquery-1.9.1.min.js', 'ressources/faster_rcnn_resnet101.config']},
      classifiers=[
            "Programming Language :: Python",
            "Development Status :: 1 - Planning",
            "License :: OSI Approved",
            "Natural Language :: French",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.6",
            "Topic :: Communications",
      ],

      )
