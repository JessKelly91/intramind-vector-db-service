"""
Setup configuration for vectordb-contracts Python package.

This package provides Python gRPC client/server code generated from Protocol Buffer
definitions for the Vector Database Service.
"""
import os
import subprocess
import sys
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.sdist import sdist


def read_version():
    """Read version from VERSION file at repository root."""
    version_file = Path(__file__).parent.parent / "VERSION"
    with open(version_file, 'r') as f:
        return f.read().strip()


def read_readme():
    """Read README for long description."""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def generate_protos():
    """Generate Python code from .proto files."""
    print("Generating protobuf code...")
    
    # Paths
    proto_dir = Path(__file__).parent.parent / "src" / "VectorDB.Contracts" / "Protos"
    output_dir = Path(__file__).parent / "vectordb_contracts"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Proto file
    proto_file = proto_dir / "vector_service.proto"
    
    if not proto_file.exists():
        print(f"ERROR: Proto file not found at {proto_file}", file=sys.stderr)
        sys.exit(1)
    
    # Generate Python code
    try:
        subprocess.check_call([
            sys.executable, '-m', 'grpc_tools.protoc',
            f'-I{proto_dir}',
            f'--python_out={output_dir}',
            f'--grpc_python_out={output_dir}',
            str(proto_file)
        ])
        print(f"✓ Generated protobuf files in {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to generate protobuf code: {e}", file=sys.stderr)
        sys.exit(1)


class BuildPyCommand(build_py):
    """Custom build command that generates protos before building."""
    
    def run(self):
        generate_protos()
        build_py.run(self)


class DevelopCommand(develop):
    """Custom develop command that generates protos for editable installs."""
    
    def run(self):
        generate_protos()
        develop.run(self)


class SDistCommand(sdist):
    """Custom sdist command that generates protos before creating source distribution."""
    
    def run(self):
        generate_protos()
        sdist.run(self)


setup(
    name='vectordb-contracts',
    version=read_version(),
    author='Jess Kelly',
    author_email='',
    description='Protocol Buffer contracts for Vector Database gRPC Service',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/JessKelly91/ai-vector-db-practice',
    project_urls={
        'Source': 'https://github.com/JessKelly91/ai-vector-db-practice',
        'Bug Reports': 'https://github.com/JessKelly91/ai-vector-db-practice/issues',
    },
    packages=find_packages(exclude=['tests', 'tests.*', 'scripts', 'scripts.*']),
    python_requires='>=3.9',
    install_requires=[
        'grpcio>=1.60.0,<2.0.0',
        'protobuf>=4.25.0,<6.0.0',
    ],
    extras_require={
        'dev': [
            'grpcio-tools>=1.60.0,<2.0.0',
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'mypy>=1.5.0',
            'build>=1.0.0',
            'twine>=4.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='grpc protobuf vectordb weaviate contracts api',
    cmdclass={
        'build_py': BuildPyCommand,
        'develop': DevelopCommand,
        'sdist': SDistCommand,
    },
    include_package_data=True,
    zip_safe=False,
    license='MIT',
)

