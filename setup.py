from setuptools import setup, find_packages

setup(name="pelican-zipwriter",
      version="0.0.1",
      description="Export your pelican site to a zip file",
      long_description="",
      url="https://github.com/gkrnours/pelican-zipwriter",
      author="gkr",
      author_email="couesl@gmail.com",
      license="ISC",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Environment :: Plugins",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
      ],
      packages=find_packages("src"),
      package_dir={"": "src"},
      install_requires=[
          "pelican",
      ],
      extras_require={
          'test': ["pytest"],
      },

)
