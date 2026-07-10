#!/usr/bin/env python3
"""
批量添加 MIT 版权头到 HexLang Python 源文件

用法：
    python scripts/add-license-header.py

说明：
    - 扫描 src/ 和 bin/ 目录下的所有 .py 文件
    - 如果文件顶部没有 MIT License 声明，则自动添加
    - 跳过已有版权文件的修改（避免重复）
"""

import os
import sys
from pathlib import Path

# Windows UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MIT_HEADER = '''"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

'''

def needs_header(file_path: str) -> bool:
    """检查文件是否已有 MIT 版权声明"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(500)  # 只读前 500 字符
            return 'MIT License' not in content and 'Copyright' not in content
    except Exception:
        return True

def add_header(file_path: str):
    """为单个文件添加 MIT 版权头"""
    with open(file_path, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(MIT_HEADER)
        f.write(existing_content)
    
    print(f"✅ 添加版权头: {file_path}")

def main():
    """主函数"""
    base_dir = Path(__file__).parent.parent
    
    # 扫描目标目录
    scan_dirs = ['src', 'bin']
    py_files = []
    
    for scan_dir in scan_dirs:
        dir_path = base_dir / scan_dir
        if dir_path.exists():
            for root, dirs, files in os.walk(dir_path):
                for f in files:
                    if f.endswith('.py'):
                        py_files.append(os.path.join(root, f))
    
    print(f"\n=== HexLang MIT 版权头批量添加 ===")
    print(f"找到 {len(py_files)} 个 Python 文件\n")
    
    added = 0
    skipped = 0
    
    for file_path in py_files:
        if needs_header(file_path):
            add_header(file_path)
            added += 1
        else:
            skipped += 1
    
    print(f"\n📊 统计:")
    print(f"  已添加: {added} 个文件")
    print(f"  已跳过: {skipped} 个文件（已有版权）")
    print(f"  总计: {len(py_files)} 个文件\n")

if __name__ == '__main__':
    main()
