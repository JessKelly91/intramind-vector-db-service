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
py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/collections_messages.proto

py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/collections_service.proto

py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/documents_messages.proto

py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/documents_service.proto

py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/search_messages.proto

py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/search_service.proto

py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/health_messages.proto

py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/Core/health_service.proto

REM Generate code for the main vector service
py -m grpc_tools.protoc ^
  -I./%PROTO_DIR% ^
  --python_out=./%OUTPUT_DIR% ^
  --grpc_python_out=./%OUTPUT_DIR% ^
  ./%PROTO_DIR%/vector_service.proto

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to generate proto files
    echo Make sure you have installed: pip install grpcio-tools
    pause
    exit /b 1
)

echo.
echo Fixing imports in generated files...

REM Fix imports in vector_service_pb2_grpc.py
py -c "import sys; f=open('src/service/protos/vector_service_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import vector_service_pb2 as','from . import vector_service_pb2 as').replace('from Core import','from .Core import'); f=open('src/service/protos/vector_service_pb2_grpc.py','w'); f.write(content); f.close(); print('Fixed vector_service_pb2_grpc.py')"

REM Fix imports in vector_service_pb2.py
py -c "import sys; f=open('src/service/protos/vector_service_pb2.py','r'); content=f.read(); f.close(); content=content.replace('from Core import','from .Core import'); f=open('src/service/protos/vector_service_pb2.py','w'); f.write(content); f.close(); print('Fixed vector_service_pb2.py')"

REM Fix imports in Core service files
py -c "import os, glob; files=glob.glob('src/service/protos/Core/*_grpc.py'); [open(f,'w').write(open(f,'r').read().replace('from Core import','from . import')) for f in files]; print(f'Fixed {len(files)} Core gRPC files')"

echo.
echo ========================================
echo SUCCESS! Proto files generated
echo ========================================
echo Generated files:
echo   - src/service/protos/Core/*_pb2.py
echo   - src/service/protos/Core/*_pb2_grpc.py
echo   - src/service/protos/vector_service_pb2.py
echo   - src/service/protos/vector_service_pb2_grpc.py
echo.
echo Note: Generated from vector-db-contracts
echo ========================================
echo.
pause
