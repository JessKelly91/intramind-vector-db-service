@echo off
REM Generate Python code from Protocol Buffer definitions

cd %~dp0\..

echo Generating Python code from .proto files...

python -m grpc_tools.protoc ^
  -I./src/service/protos ^
  --python_out=./src/service/protos ^
  --grpc_python_out=./src/service/protos ^
  ./src/service/protos/vector_service.proto

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Fixing imports in generated files...
    python -c "import sys; f=open('src/service/protos/vector_service_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import vector_service_pb2 as','from . import vector_service_pb2 as'); f=open('src/service/protos/vector_service_pb2_grpc.py','w'); f.write(content); f.close(); print('Fixed imports')"
    echo.
    echo Success! Generated files:
    echo   - src/service/protos/vector_service_pb2.py
    echo   - src/service/protos/vector_service_pb2_grpc.py
    echo.
    echo You can now use these in your Python code.
) else (
    echo.
    echo Error: Failed to generate proto files
    echo Make sure you have installed: pip install grpcio-tools
)

pause
