#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断脚本 - 检查模型切换问题
"""

import requests
import time
import sys

def test_model_switching():
    """测试模型切换功能"""
    server_url = "http://localhost:5000"
    
    print("=== 模型切换诊断 ===\n")
    
    # 1. 检查服务器连接
    print("1. 检查服务器连接...")
    try:
        response = requests.get(f"{server_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 服务器运行正常")
            print(f"   当前模型: {data['model_size']}")
            print(f"   模型已加载: {data['model_loaded']}")
            print(f"   正在加载: {data['is_loading']}")
        else:
            print(f"   ✗ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ 无法连接服务器: {e}")
        print("   请确保服务器正在运行 (python server.py)")
        return False
    
    # 2. 测试模型切换
    models_to_test = ["tiny", "base", "small"]
    
    for model in models_to_test:
        print(f"\n2. 测试切换到 {model} 模型...")
        
        try:
            # 发送模型加载请求
            start_time = time.time()
            response = requests.post(f"{server_url}/api/load_model", 
                                   json={"model_size": model}, timeout=120)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    print(f"   ✓ {model} 模型加载成功 (耗时: {end_time - start_time:.1f}秒)")
                    
                    # 验证模型是否真的切换了
                    status_response = requests.get(f"{server_url}/api/status", timeout=5)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data['model_size'] == model and status_data['model_loaded']:
                            print(f"   ✓ 模型状态验证成功")
                        else:
                            print(f"   ✗ 模型状态验证失败")
                            print(f"     期望: {model}, 实际: {status_data['model_size']}")
                            return False
                else:
                    print(f"   ✗ {model} 模型加载失败: {data['message']}")
                    return False
            else:
                print(f"   ✗ 请求失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"     错误信息: {error_data}")
                except:
                    print(f"     响应内容: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ✗ {model} 模型加载超时 (>120秒)")
            return False
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 请求错误: {e}")
            return False
    
    print(f"\n✓ 所有模型切换测试通过！")
    return True

def check_dependencies():
    """检查依赖"""
    print("3. 检查依赖包...")
    
    try:
        import whisper
        print("   ✓ whisper")
    except ImportError:
        print("   ✗ whisper (运行: pip install openai-whisper)")
        return False
    
    try:
        import flask
        print("   ✓ flask")
    except ImportError:
        print("   ✗ flask (运行: pip install flask)")
        return False
    
    try:
        import requests
        print("   ✓ requests")
    except ImportError:
        print("   ✗ requests (运行: pip install requests)")
        return False
    
    return True

def main():
    print("开始诊断模型切换问题...\n")
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装缺失的依赖包")
        return
    
    # 测试模型切换
    success = test_model_switching()
    
    if success:
        print("\n=== 诊断结果 ===")
        print("✓ 模型切换功能正常")
        print("如果客户端仍然无法切换模型，请尝试:")
        print("1. 重启客户端程序")
        print("2. 检查网络连接")
        print("3. 查看客户端错误信息")
    else:
        print("\n=== 诊断结果 ===")
        print("✗ 发现模型切换问题")
        print("建议解决方案:")
        print("1. 重启服务器: python server.py")
        print("2. 检查服务器日志输出")
        print("3. 确保有足够的内存和磁盘空间")
        print("4. 检查防火墙设置")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n诊断被用户中断")
    except Exception as e:
        print(f"\n诊断过程中出现错误: {e}")
    
    input("\n按回车键退出...")