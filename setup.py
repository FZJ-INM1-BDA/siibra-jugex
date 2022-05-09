from setuptools import setup, find_packages
import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_version():
    path_to_init=os.path.join(ROOT_DIR, 'siibra_jugex', '__init__.py')
    with open(path_to_init, 'r', encoding="utf-8") as f:
        content=f.read()
        version_match=re.search(r"^__version__=['\"](.*?)['\"]$", content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError('version cannot be found!')

with open(os.path.join(ROOT_DIR,"README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="siibra_jugex",
    version=find_version(),
    author="Big Data Analytics Group and S. Bludau, Forschungszentrum Juelich, Institute of Neuroscience and Medicine (INM-1)",
    author_email="inm1-bda@fz-juelich.de",
    description="siibra-jugex - Differential analysis of gene expression in brain regions using the siibra framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FZJ-INM1-BDA/siibra-jugex",
    packages=find_packages(include=['siibra_jugex']),
    include_package_data=True,
    # packages=find_packages(include=['.']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
    install_requires=['siibra>=0.3a17','statsmodels','scipy']
)

