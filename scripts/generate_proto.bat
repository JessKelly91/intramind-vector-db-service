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
