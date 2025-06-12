#!/usr/bin/env python3
"""
统一测试运行器
运行所有开发测试
"""
import subprocess
import sys
import glob
from pathlib import Path

def run_tests():
    """运行所有测试"""
    print("🧪 EMC知识图谱系统 - 综合测试")
    print("=" * 50)
    
    test_dir = Path(__file__).parent
    test_files = glob.glob(str(test_dir / "test_*.py"))
    
    if not test_files:
        print("❌ 未找到测试文件")
        return
    
    print(f"📋 发现 {len(test_files)} 个测试文件")
    
    passed = 0
    failed = 0
    
    for test_file in sorted(test_files):
        test_name = Path(test_file).stem
        print(f"\n🔍 运行测试: {test_name}")
        print("-" * 30)
        
        try:
            result = subprocess.run([
                sys.executable, test_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {test_name} - 通过")
                passed += 1
            else:
                print(f"❌ {test_name} - 失败")
                print("错误输出:", result.stderr[:200])
                failed += 1
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} - 超时")
            failed += 1
        except Exception as e:
            print(f"💥 {test_name} - 异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 通过率: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "无测试")
    
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")

if __name__ == "__main__":
    run_tests()