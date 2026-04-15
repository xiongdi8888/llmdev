from calc import add

# 加算関数 add のテスト
def test_add():
    result = add(2, 3)
    assert result == 5

def test_basic():
    # 値の一致を確認
    assert 1 + 1 == 2

    # リストや辞書の要素が含まれているか確認
    assert "apple" in ["apple", "banana", "cherry"]
    assert "key" in {"key": "value"}

    # 条件の評価
    assert True is True
    assert not False

    # 等価比較
    assert 3 == 3

    # 不等比較
    assert 3 != 4

    # 値が指定範囲にあるか
    assert 5 > 2
    assert 2 < 5
    assert 4 >= 4
    assert 3 <= 5

    # 複数のアサーション
    assert all([2 + 2 == 4, 3 * 3 == 9])
    assert any([False, 1 + 1 == 2, False])

import pytest
# 同じ関数を異なる入力で繰り返しテスト
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (10, 5, 15),
])

def test_add_param(a, b, expected):
    assert add(a, b) == expected

# bが0の場合、ValueErrorを発生させる除算関数
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# 0で除算したときにValueErrorが発生するかをテスト
def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)

# 通常の除算が正しく行われるかをテスト
def test_divide_normal():
    result = divide(10, 2)
    assert result == 5


#import pytest
import calc

# 加算関数 add のテスト
def test_add():
    assert calc.add(2, 3) == 5
    assert calc.add(-5, -3) == -8
    assert calc.add(7, -2) == 5
    assert calc.add(0, 5) == 5
    assert calc.add(3, 0) == 3

# 減算関数 subtract のテスト
def test_subtract():
    assert calc.subtract(5, 3) == 2
    assert calc.subtract(-3, -5) == 2
    assert calc.subtract(7, -2) == 9
    assert calc.subtract(5, 0) == 5
    assert calc.subtract(0, 3) == -3

# 乗算関数 multiply のテスト
def test_multiply():
    assert calc.multiply(2, 3) == 6
    assert calc.multiply(-2, -3) == 6
    assert calc.multiply(2, -3) == -6
    assert calc.multiply(5, 0) == 0
    assert calc.multiply(0, 3) == 0

# 除算関数 divide のテスト
def test_divide():
    assert calc.divide(6, 3) == 2
    assert calc.divide(-6, -3) == 2
    assert calc.divide(6, -3) == -2

# 除算関数 divide が0で除算された場合にエラーを返すことを検証する
def test_divide_by_zero():
    with pytest.raises(ValueError, match="0で除算された"):
        calc.divide(5, 0)
    with pytest.raises(ValueError, match="0で除算された"):
        calc.divide(0, 0)


# 加算関数 add のテスト
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-5, -3, -8),
    (7, -2, 5),
    (0, 5, 5),
    (3, 0, 3)
])
def test_add2(a, b, expected):
    assert calc.add(a, b) == expected

# 減算関数 subtract のテスト
@pytest.mark.parametrize("a, b, expected", [
    (5, 3, 2),
    (-3, -5, 2),
    (7, -2, 9),
    (5, 0, 5),
    (0, 3, -3)
])
def test_subtract2(a, b, expected):
    assert calc.subtract(a, b) == expected

# 乗算関数 multiply のテスト
@pytest.mark.parametrize2("a, b, expected", [
    (2, 3, 6),
    (-2, -3, 6),
    (2, -3, -6),
    (5, 0, 0),
    (0, 3, 0)
])
def test_multiply(a, b, expected):
    assert calc.multiply(a, b) == expected

# 除算関数 divide のテスト
@pytest.mark.parametrize2("a, b, expected", [
    (6, 3, 2),
    (-6, -3, 2),
    (6, -3, -2)
])
def test_divide(a, b, expected):
    assert calc.divide(a, b) == expected

# 除算関数 divide が0で除算された場合にエラーを返すことを検証する
@pytest.mark.parametrize2("a, b", [
    (5, 0),
    (0, 0)
])
def test_divide_by_zero2(a, b):
    with pytest.raises(ValueError, match="0で除算された"):
        calc.divide(a, b)