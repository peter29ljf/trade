#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""
check_environment.py - 检查Python环境配置

该脚本检查当前Python环境是否正确配置，包括所有必要的依赖。
"""

import sys
import os
import platform
import json

# 检查Python版本
def check_python_version():
    print(f"Python版本: {platform.python_version()}")
    print(f"Python路径: {sys.executable}")
    print(f"使用Python 3.12: {'是' if sys.version_info.major == 3 and sys.version_info.minor >= 12 else '否'}")
    print()

# 检查依赖
def check_dependencies():
    try:
        # 导入主要依赖
        import dotenv
        import requests
        import urllib3
        
        print("基础依赖检查:")
        # python-dotenv模块版本获取方式不同
        try:
            print(f"- dotenv: {dotenv.__version__}")
        except AttributeError:
            # 尝试另一种方式获取版本
            try:
                from importlib.metadata import version
                print(f"- dotenv: {version('python-dotenv')}")
            except:
                print("- dotenv: 已安装，但无法获取版本号")
        
        print(f"- requests: {requests.__version__}")
        print(f"- urllib3: {urllib3.__version__}")
        
        # 尝试导入加密相关依赖
        try:
            import cryptography
            print(f"- cryptography: {cryptography.__version__}")
        except ImportError:
            print("- cryptography: 未安装")
        
        # 尝试导入web3相关依赖
        try:
            import web3
            print(f"- web3: {web3.__version__}")
        except ImportError:
            print("- web3: 未安装")
        
        print()
        return True
    except ImportError as e:
        print(f"依赖检查失败: {str(e)}")
        return False

# 检查文件权限
def check_file_permissions():
    print("文件权限检查:")
    files_to_check = [
        "execute_initial_buy.py",
        "execute_next_buy.py",
        "market_buy_order.py",
        "check_price.py",
        "math_utils.py"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            is_executable = os.access(file, os.X_OK)
            print(f"- {file}: {'可执行' if is_executable else '不可执行'}")
        else:
            print(f"- {file}: 文件不存在")
    
    print()

# 检查环境变量配置
def check_env_config():
    print("环境变量检查:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        env_vars = [
            "POLYMARKET_HOST",
            "POLYMARKET_API_KEY",
            "POLYMARKET_PASSWORD",
            "PRIVATE_KEY"
        ]
        
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                # 隐藏敏感信息
                if var in ["POLYMARKET_API_KEY", "POLYMARKET_PASSWORD", "PRIVATE_KEY"]:
                    print(f"- {var}: {'*' * (len(value) if len(value) < 10 else 10)}")
                else:
                    print(f"- {var}: {value}")
            else:
                print(f"- {var}: 未设置")
        
        return True
    except Exception as e:
        print(f"环境变量检查失败: {str(e)}")
        return False

# 测试网络连接
def test_network():
    print("网络连接测试:")
    try:
        import requests
        url = "https://clob.polymarket.com"
        response = requests.get(url, timeout=5)
        print(f"- Polymarket API: {'可访问' if response.status_code == 200 else f'状态码 {response.status_code}'}")
        return True
    except Exception as e:
        print(f"- Polymarket API: 连接失败 - {str(e)}")
        return False

# 检查目录结构
def check_directory_structure():
    print("目录结构检查:")
    dirs_to_check = [
        "data",
        "py-clob-client"
    ]
    
    for dir_name in dirs_to_check:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"- {dir_name}: 存在")
        else:
            print(f"- {dir_name}: 不存在")
    
    print()

# 主函数
def main():
    print("========== Python环境检查 ==========")
    check_python_version()
    check_dependencies()
    check_file_permissions()
    check_env_config()
    check_directory_structure()
    test_network()
    print("\n环境检查完成!\n")

if __name__ == "__main__":
    main() 