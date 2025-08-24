import re
from src.ui.formatters import MathFormatter


def test_inline_frac_and_greek():
    s = "This is inline math $\\frac{1}{2} + \\alpha$ in text."
    out = MathFormatter.transform_math_regions(s)
    assert "(1)/(2)" in out
    assert "α" in out


def test_display_sqrt():
    s = "Display math here:\n\\[\\sqrt{2} + \\pi\\] rest"
    out = MathFormatter.transform_math_regions(s)
    assert "√(2)" in out
    assert "π" in out


def test_no_math_unchanged():
    s = "No math here, just text."
    out = MathFormatter.transform_math_regions(s)
    assert out == s
