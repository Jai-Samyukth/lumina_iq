# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Add the backend directory to Python path
sys.path.insert(0, str(current_dir))

block_cipher = None

# Define data files to include
datas = [
    # Include config directory
    ('config', 'config'),
    # Include api_rotation directory from parent
    ('../api_rotation', 'api_rotation'),
    # Include any template files if they exist
    # ('templates', 'templates'),
    # Include static files if they exist
    # ('static', 'static'),
]

# Hidden imports for FastAPI and dependencies
hiddenimports = [
    'fastapi',
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'starlette',
    'starlette.applications',
    'starlette.middleware',
    'starlette.middleware.cors',
    'starlette.routing',
    'starlette.responses',
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'pydantic.types',
    'pydantic.validators',
    'python_multipart',
    'jose',
    'jose.jwt',
    'passlib',
    'passlib.hash',
    'passlib.context',
    'google.generativeai',
    'PyPDF2',
    'pdfplumber',
    'aiofiles',
    'aiohttp',
    'dotenv',
    'asyncio',
    'logging',
    'json',
    'pathlib',
    'socket',
    'platform',
    'contextlib',
    # Include all route modules
    'routes',
    'routes.auth',
    'routes.pdf',
    'routes.chat',
    # Include all model modules
    'models',
    'models.auth',
    'models.chat',
    'models.pdf',
    # Include all service modules
    'services',
    'services.auth_service',
    'services.chat_service',
    'services.pdf_service',
    # Include all utility modules
    'utils',
    'utils.cache',
    'utils.ip_detector',
    'utils.logger',
    'utils.logging_config',
    'utils.security',
    'utils.storage',
    # Include api_rotation module
    'api_rotation',
    'api_rotation.api_key_rotator',
]

a = Analysis(
    ['main.py'],
    pathex=[str(current_dir), str(current_dir.parent)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='luminaiq-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
