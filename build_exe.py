#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
블로그 생성기 v2.0 - 최적화된 빌드 스크립트
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_files():
    """Clean existing build files"""
    print("Cleaning existing build files...")
    
    folders_to_clean = ['build', 'dist', '__pycache__', 'BlogGenerator_Distribution']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Removed {folder} folder")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    print("   Cleanup completed\n")

def install_dependencies():
    """Install dependency packages"""
    print("Installing dependency packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("   Package installation completed\n")
    except subprocess.CalledProcessError as e:
        print(f"   Package installation failed: {e}")
        return False
    return True

def create_spec_file():
    """PyInstaller spec 파일 생성"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
import sys
sys.setrecursionlimit(5000)

a = Analysis(
    ['blog_generator.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets', 
        'PyQt5.QtGui',
        'requests',
        'google.generativeai',
        'selenium',
        'webdriver_manager',
        'pyperclip',
        'core.workers',
        'core.tistory_manager',
        'tabs.title_generation_tab',
        'tabs.content_generation_tab',
        'tabs.blog_publish_tab',
        'utils.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BlogGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('BlogGenerator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("   Spec file created successfully")

def build_executable():
    """Build executable file"""
    print("Building executable file...")
    
    try:
        # Build with spec file
        subprocess.check_call(['pyinstaller', 'BlogGenerator.spec'])
        
        if os.path.exists('dist/BlogGenerator.exe'):
            print("   Build successful!")
            return True
        else:
            print("   Build failed - exe file not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   Build failed: {e}")
        return False

def create_distribution():
    """Create distribution folder"""
    print("\nCreating distribution folder...")
    
    dist_folder = 'BlogGenerator_Distribution'
    os.makedirs(dist_folder, exist_ok=True)
    
    # Copy essential files
    files_to_copy = [
        ('dist/BlogGenerator.exe', 'BlogGenerator.exe'),
        ('README.md', 'README.md'),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            dst_path = os.path.join(dist_folder, dst)
            shutil.copy2(src, dst_path)
            print(f"   Copied {src} to {dst_path}")
    
    # Create usage guide
    create_usage_guide(dist_folder)
    
    print(f"\nDistribution folder '{dist_folder}' created successfully!")
    print("   You can distribute this entire folder.")



def create_usage_guide(folder):
    """사용법 가이드 생성"""
    guide_content = '''# 블로그 글 자동 생성기 v2.0 사용법

## 🚀 시작하기

### 1단계: API 키 설정
프로그램 실행 후 설정 메뉴에서 다음 정보를 입력하세요:
   - 네이버 검색 API 키 (Client ID, Client Secret)
   - Google Gemini API 키

### 2단계: 프로그램 실행
`BlogGenerator.exe` 파일을 더블클릭하여 실행하세요.

### 3단계: 사용하기
1. **제목 생성 탭**:
   - 키워드를 입력하고 검색
   - 원하는 블로그 글을 선택 (체크박스)
   - 제목 생성 버튼 클릭

2. **글 생성 탭**:
   - 생성된 제목을 선택
   - 글 생성 버튼 클릭
   - 생성된 글을 편집 및 저장

3. **블로그 발행 탭**:
   - 티스토리 계정 연동
   - 글 자동 발행

## 📋 API 키 발급 방법

### 네이버 검색 API
1. https://developers.naver.com/main/ 접속
2. "애플리케이션 등록" 클릭
3. 애플리케이션 정보 입력
4. "검색" API 선택
5. Client ID, Client Secret 복사

### Google Gemini API
1. https://aistudio.google.com/ 접속
2. "Get API key" 클릭
3. 새 프로젝트 생성 또는 기존 프로젝트 선택
4. API 키 생성 및 복사

## ❓ 문제 해결

### 프로그램이 실행되지 않는 경우
- Windows Defender나 백신 프로그램에서 차단했을 수 있습니다
- 프로그램을 "신뢰할 수 있는 프로그램"으로 추가하세요
- 관리자 권한으로 실행해보세요

### API 오류가 발생하는 경우
- 설정에서 입력한 API 키가 올바른지 확인하세요
- 네이버 API 일일 할당량을 확인하세요 (25,000회/일)
- Gemini API 키가 활성화되어 있는지 확인하세요

### 크롬 브라우저 오류
- 시스템에 Chrome 브라우저가 설치되어 있는지 확인하세요
- Chrome을 최신 버전으로 업데이트하세요

## 📞 지원
문제가 있으면 개발자에게 문의하세요.

---
블로그 생성기 v2.0
'''
    
    with open(os.path.join(folder, '사용법.txt'), 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("   Usage guide file created")

def main():
    """Main build process"""
    print("Blog Generator v2.0 Build Started...\n")
    
    # 1. Clean existing files
    clean_build_files()
    
    # 2. Install dependencies
    if not install_dependencies():
        return False
    
    # 3. Create spec file
    create_spec_file()
    
    # 4. Build executable
    if not build_executable():
        return False
    
    # 5. Create distribution folder
    create_distribution()
    
    print("\nBuild completed successfully!")
    print("Check BlogGenerator_Distribution folder.")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nBuild failed")
        sys.exit(1)