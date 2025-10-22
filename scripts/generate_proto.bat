@echo off
REM Generate Python code from Protocol Buffer definitions
REM Now generates from vector-db-contracts (single source of truth)

cd %~dp0\..

echo Generating Python code from .proto files...
echo Source: vector-db-contracts/src/VectorDB.Contracts/Protos/
echo.

REM Define paths
set PROTO_DIR=vector-db-contracts/src/VectorDB.Contracts/Protos
set OUTPUT_DIR=src/service/protos

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%OUTPUT_DIR%\Core" mkdir "%OUTPUT_DIR%\Core"

REM Generate code for all Core proto files
python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/collections_messages.proto

python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/collections_service.proto

python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/documents_messages.proto

python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/documents_service.proto

python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/search_messages.proto

python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/search_service.proto

python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/health_messages.proto

python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/health_service.proto

REM Generate code for the main vector service
python -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/vector_service.proto

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Fixing imports in generated files...
    python -c "import sys; f=open('src/service/protos/vector_service_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import vector_service_pb2 as','from . import vector_service_pb2 as'); f=open('src/service/protos/vector_service_pb2_grpc.py','w'); f.write(content); f.close(); print('Fixed imports')"
    echo.
    echo Success! Generated files:
    echo   - src/service/protos/Core/*_pb2.py
    echo   - src/service/protos/Core/*_pb2_grpc.py
    echo   - src/service/protos/vector_service_pb2.py
    echo   - src/service/protos/vector_service_pb2_grpc.py
    echo.
    echo Note: These are generated from vector-db-contracts (single source of truth)
) else (
    echo.
    echo Error: Failed to generate proto files
    echo Make sure you have installed: pip install grpcio-tools
)

pause
