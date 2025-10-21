#!/usr/bin/env python3
"""
Build and validate the vectordb-contracts Python package.

This script:
1. Generates protobuf code
2. Builds the package (wheel + source distribution)
3. Validates the package contents
4. Optionally installs locally for testing

Usage:
    python scripts/build_package.py [--install]
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'=' * 70}")
    print(f"{description}")
    print(f"{'=' * 70}")
    print(f"Command: {' '.join(str(c) for c in cmd)}\n")
    
    try:
        subprocess.check_call(cmd)
        print(f"✓ {description} - SUCCESS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (return code: {e.returncode})\n", file=sys.stderr)
        return False


def clean_build_artifacts(python_root):
    """Remove build artifacts."""
    print("\n" + "=" * 70)
    print("Cleaning build artifacts")
    print("=" * 70)
    
    dirs_to_remove = [
        python_root / "build",
        python_root / "dist",
        python_root / "vectordb_contracts.egg-info",
    ]
    
    for dir_path in dirs_to_remove:
        if dir_path.exists():
            print(f"Removing: {dir_path}")
            shutil.rmtree(dir_path)
    
    print("✓ Build artifacts cleaned\n")


def main():
    """Main build script."""
    parser = argparse.ArgumentParser(description="Build vectordb-contracts package")
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install the package locally after building'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts before building'
    )
    args = parser.parse_args()
    
    # Get paths
    script_dir = Path(__file__).parent
    python_root = script_dir.parent
    
    print("=" * 70)
    print("vectordb-contracts Package Build Script")
    print("=" * 70)
    print(f"Python package root: {python_root.absolute()}")
    print()
    
    # Clean if requested
    if args.clean:
        clean_build_artifacts(python_root)
    
    # Step 1: Generate protos
    generate_script = script_dir / "generate_protos.py"
    if not run_command(
        [sys.executable, str(generate_script)],
        "Step 1: Generate protobuf code"
    ):
        return 1
    
    # Step 2: Build package
    if not run_command(
        [sys.executable, '-m', 'build', str(python_root)],
        "Step 2: Build package (wheel + sdist)"
    ):
        print("\nMake sure you have 'build' installed:", file=sys.stderr)
        print("  pip install build\n", file=sys.stderr)
        return 1
    
    # Step 3: Check package with twine
    dist_dir = python_root / "dist"
    if dist_dir.exists():
        if not run_command(
            [sys.executable, '-m', 'twine', 'check', f'{dist_dir}/*'],
            "Step 3: Validate package with twine"
        ):
            print("\nMake sure you have 'twine' installed:", file=sys.stderr)
            print("  pip install twine\n", file=sys.stderr)
            return 1
    
    # Step 4: List built files
    print("\n" + "=" * 70)
    print("Built packages:")
    print("=" * 70)
    if dist_dir.exists():
        for file in sorted(dist_dir.iterdir()):
            size = file.stat().st_size / 1024  # KB
            print(f"  {file.name} ({size:.1f} KB)")
    print()
    
    # Step 5: Install locally if requested
    if args.install:
        # Find the wheel file
        wheel_files = list(dist_dir.glob("*.whl"))
        if wheel_files:
            wheel_file = wheel_files[0]
            if not run_command(
                [sys.executable, '-m', 'pip', 'install', '--force-reinstall', str(wheel_file)],
                "Step 5: Install package locally"
            ):
                return 1
            
            # Test import
            print("\n" + "=" * 70)
            print("Testing import")
            print("=" * 70)
            test_result = subprocess.run(
                [sys.executable, '-c', 
                 'from vectordb_contracts import vector_service_pb2, vector_service_pb2_grpc; '
                 'print("✓ Successfully imported vectordb_contracts modules")'],
                capture_output=True,
                text=True
            )
            
            if test_result.returncode == 0:
                print(test_result.stdout)
            else:
                print(f"❌ Import test failed:\n{test_result.stderr}", file=sys.stderr)
                return 1
    
    print("\n" + "=" * 70)
    print("✓ BUILD COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Test locally: pip install dist/*.whl")
    print("  2. Upload to TestPyPI: twine upload --repository testpypi dist/*")
    print("  3. Install from TestPyPI: pip install --index-url https://test.pypi.org/simple/ vectordb-contracts")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

