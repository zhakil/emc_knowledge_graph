import pytest

def pytest_configure(config):
    # 强制使用 PyQt5 作为默认后端
    import os
    os.environ['PYTEST_QT_API'] = 'pyqt5' 