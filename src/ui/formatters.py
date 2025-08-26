"""UI formatters for text processing."""
import re
from typing import Optional


class MathFormatter:
    r"""Enhanced math transformer with pre-filtering and robust LaTeX support.

    Efficiently processes LaTeX math expressions for terminal display by:
    1. Pre-checking for math content to skip unnecessary processing
    2. Converting common LaTeX constructs to Unicode/ASCII equivalents
    3. Providing graceful fallbacks for unsupported expressions
    """

    # Extended Greek letters support
    GREEK = {
        r"\\alpha": "α", r"\\Alpha": "Α",
        r"\\beta": "β", r"\\Beta": "Β", 
        r"\\gamma": "γ", r"\\Gamma": "Γ",
        r"\\delta": "δ", r"\\Delta": "Δ",
        r"\\epsilon": "ε", r"\\varepsilon": "ε",
        r"\\zeta": "ζ", r"\\Zeta": "Ζ",
        r"\\eta": "η", r"\\Eta": "Η",
        r"\\theta": "θ", r"\\Theta": "Θ", r"\\vartheta": "ϑ",
        r"\\iota": "ι", r"\\Iota": "Ι",
        r"\\kappa": "κ", r"\\Kappa": "Κ",
        r"\\lambda": "λ", r"\\Lambda": "Λ",
        r"\\mu": "μ", r"\\Mu": "Μ",
        r"\\nu": "ν", r"\\Nu": "Ν",
        r"\\xi": "ξ", r"\\Xi": "Ξ",
        r"\\omicron": "ο", r"\\Omicron": "Ο",
        r"\\pi": "π", r"\\Pi": "Π", r"\\varpi": "ϖ",
        r"\\rho": "ρ", r"\\Rho": "Ρ", r"\\varrho": "ϱ",
        r"\\sigma": "σ", r"\\Sigma": "Σ", r"\\varsigma": "ς",
        r"\\tau": "τ", r"\\Tau": "Τ",
        r"\\upsilon": "υ", r"\\Upsilon": "Υ",
        r"\\phi": "φ", r"\\Phi": "Φ", r"\\varphi": "ϕ",
        r"\\chi": "χ", r"\\Chi": "Χ",
        r"\\psi": "ψ", r"\\Psi": "Ψ",
        r"\\omega": "ω", r"\\Omega": "Ω",
    }

    # Extended mathematical symbols
    SYMBOLS = {
        r"\\times": "×", r"\\cdot": "·", r"\\bullet": "•",
        r"\\leq": "≤", r"\\le": "≤", r"\\geq": "≥", r"\\ge": "≥",
        r"\\neq": "≠", r"\\ne": "≠", r"\\equiv": "≡",
        r"\\pm": "±", r"\\mp": "∓",
        r"\\approx": "≈", r"\\sim": "∼", r"\\simeq": "≃",
        r"\\propto": "∝", r"\\infty": "∞",
        r"\\in": "∈", r"\\notin": "∉", r"\\ni": "∋",
        r"\\subset": "⊂", r"\\supset": "⊃", r"\\subseteq": "⊆", r"\\supseteq": "⊇",
        r"\\cup": "∪", r"\\cap": "∩", r"\\setminus": "∖",
        r"\\emptyset": "∅", r"\\varnothing": "∅",
        r"\\forall": "∀", r"\\exists": "∃", r"\\nexists": "∄",
        r"\\therefore": "∴", r"\\because": "∵",
        r"\\sum": "Σ", r"\\prod": "Π", r"\\int": "∫",
        r"\\partial": "∂", r"\\nabla": "∇",
        r"\\rightarrow": "→", r"\\to": "→", r"\\leftarrow": "←",
        r"\\leftrightarrow": "↔", r"\\Rightarrow": "⇒", r"\\Leftarrow": "⇐",
        r"\\Leftrightarrow": "⇔", r"\\iff": "⇔",
        r"\\uparrow": "↑", r"\\downarrow": "↓", r"\\updownarrow": "↕",
    }

    @staticmethod
    def has_math_content(text: str) -> bool:
        """Pre-filter: quickly check if text contains math expressions."""
        if not text:
            return False
        return '$' in text or '\\[' in text or '\\(' in text

    @staticmethod
    def _safe_transform_expr(expr: str) -> str:
        """Transform LaTeX expression with error handling and enhanced support."""
        if not expr or not expr.strip():
            return expr

        try:
            original_expr = expr
            
            # Handle nested fractions with improved regex
            def frac_repl(match):
                try:
                    num = match.group(1).strip()
                    den = match.group(2).strip()
                    return f"({num})/({den})"
                except Exception:
                    return match.group(0)  # Return original if parsing fails

            # Process fractions (handles simple nesting)
            expr = re.sub(r'\\frac\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', 
                         frac_repl, expr)

            # Handle square roots with improved pattern
            def sqrt_repl(match):
                try:
                    content = match.group(1).strip()
                    return f"√({content})"
                except Exception:
                    return match.group(0)

            expr = re.sub(r'\\sqrt\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', sqrt_repl, expr)

            # Handle superscripts and subscripts
            expr = re.sub(r'\^(\w|\{[^}]*\})', lambda m: f"^{m.group(1).strip('{}')}", expr)
            expr = re.sub(r'_(\w|\{[^}]*\})', lambda m: f"_{m.group(1).strip('{}')}", expr)

            # Apply Greek letters (case-sensitive, whole word)
            for latex_cmd, unicode_char in MathFormatter.GREEK.items():
                expr = re.sub(latex_cmd + r'(?![a-zA-Z])', unicode_char, expr)

            # Apply mathematical symbols (case-sensitive, whole word)
            for latex_cmd, unicode_char in MathFormatter.SYMBOLS.items():
                expr = re.sub(latex_cmd + r'(?![a-zA-Z])', unicode_char, expr)

            # Clean up remaining LaTeX commands (remove unknown commands gracefully)
            expr = re.sub(r'\\[a-zA-Z]+\*?', '', expr)

            # Clean up braces and excessive whitespace
            expr = re.sub(r'\{([^{}]*)\}', r'\1', expr)  # Remove simple braces
            expr = re.sub(r'\s+', ' ', expr)  # Collapse whitespace
            expr = expr.strip()

            return expr if expr else original_expr

        except Exception:
            # If any error occurs, return the original expression
            return original_expr

    @staticmethod
    def transform_math_regions(text: str) -> str:
        r"""Find and transform math regions with enhanced performance and error handling.

        Processes inline ($...$), display (\[...\]), and parenthesized (\(...\)) math.
        Includes pre-filtering for performance optimization.
        """
        if not text or not MathFormatter.has_math_content(text):
            return text

        try:
            # Handle display math \[ ... \] (highest priority)
            def display_repl(match):
                try:
                    inner = match.group(1)
                    return MathFormatter._safe_transform_expr(inner)
                except Exception:
                    return match.group(0)  # Return original on error

            text = re.sub(r'\\\[(.+?)\\\]', display_repl, text, flags=re.DOTALL)

            # Handle parenthesized math \( ... \)
            def paren_repl(match):
                try:
                    inner = match.group(1)
                    return MathFormatter._safe_transform_expr(inner)
                except Exception:
                    return match.group(0)

            text = re.sub(r'\\\((.+?)\\\)', paren_repl, text, flags=re.DOTALL)

            # Handle inline math $...$ (most common, process last to avoid conflicts)
            def inline_repl(match):
                try:
                    inner = match.group(1)
                    return MathFormatter._safe_transform_expr(inner)
                except Exception:
                    return match.group(0)

            text = re.sub(r'\$(.+?)\$', inline_repl, text, flags=re.DOTALL)

            return text

        except Exception:
            # If any catastrophic error occurs, return original text
            return text

    @staticmethod
    def clean_latex_math(text: str) -> str:
        """Compatibility wrapper for existing callers.

        Delegates to transform_math_regions which implements the enhanced
        math transformation with pre-filtering and error handling.
        """
        return MathFormatter.transform_math_regions(text)
