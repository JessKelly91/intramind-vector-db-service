#!/usr/bin/env python3
"""
Generate Python gRPC code from Protocol Buffer definitions.

This script generates Python protobuf and gRPC code from the .proto files
located in the C# project (single source of truth).

Usage:
    python scripts/generate_protos.py
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Generate protobuf Python code from .proto files."""
    # Get paths relative to this script
    script_dir = Path(__file__).parent
    python_root = script_dir.parent
    contracts_root = python_root.parent
    
    # Source: C# project protos (single source of truth)
    proto_dir = contracts_root / "src" / "VectorDB.Contracts" / "Protos"
    
    # Output: Python package directory
    output_dir = python_root / "vectordb_contracts"
    
    # Validate proto directory exists
    if not proto_dir.exists():
        print(f"❌ ERROR: Proto directory not found at: {proto_dir}", file=sys.stderr)
        print(f"   Expected path: {proto_dir.absolute()}", file=sys.stderr)
        sys.exit(1)
    
    # Find all proto files (including Core subdirectory)
    proto_files = []
    proto_files.extend(proto_dir.glob("*.proto"))
    proto_files.extend(proto_dir.glob("Core/*.proto"))
    
    if not proto_files:
        print(f"❌ ERROR: No .proto files found in: {proto_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Generating Python gRPC code from Protocol Buffers")
    print("=" * 70)
    print(f"Proto source dir: {proto_dir.relative_to(contracts_root)}")
    print(f"Output dir:       {output_dir.relative_to(contracts_root)}")
    print(f"Proto files found: {len(proto_files)}")
    print()
    
    # Generate Python code using grpc_tools.protoc
    try:
        # Convert all proto files to relative paths for the command
        proto_file_paths = [str(f.relative_to(proto_dir)) for f in proto_files]
        
        cmd = [
            sys.executable, '-m', 'grpc_tools.protoc',
            f'-I{proto_dir}',
            f'--python_out={output_dir}',
            f'--grpc_python_out={output_dir}',
        ] + proto_file_paths
        
        print("Running command:")
        print(f"  {' '.join(str(c) for c in cmd[:4])}")
        for pf in proto_file_paths:
            print(f"    {pf}")
        print()
        
        subprocess.check_call(cmd, cwd=proto_dir)
        
        print("✓ Successfully generated protobuf files:")
        # List generated files
        for proto_file in proto_files:
            stem = proto_file.stem
            rel_path = proto_file.relative_to(proto_dir)
            parent = rel_path.parent
            if parent != Path('.'):
                print(f"  - {output_dir / parent / f'{stem}_pb2.py'}")
                print(f"  - {output_dir / parent / f'{stem}_pb2_grpc.py'}")
            else:
                print(f"  - {output_dir / f'{stem}_pb2.py'}")
                print(f"  - {output_dir / f'{stem}_pb2_grpc.py'}")
        print()
        print("You can now import these in your Python code:")
        print("  from vectordb_contracts import vector_service_pb2")
        print("  from vectordb_contracts import vector_service_pb2_grpc")
        print()
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to generate protobuf code", file=sys.stderr)
        print(f"   Return code: {e.returncode}", file=sys.stderr)
        print()
        print("Make sure you have installed grpcio-tools:", file=sys.stderr)
        print("  pip install grpcio-tools", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find Python interpreter or grpc_tools", file=sys.stderr)
        print()
        print("Make sure you have installed grpcio-tools:", file=sys.stderr)
        print("  pip install grpcio-tools", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

