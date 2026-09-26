import sys
import os

# Папка src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import check_matrix

def test_check_matrix_exists():
    # Проверка существования функции
    assert check_matrix is not None
