"""Shared, approximate, per-language patterns for the slop scripts. Portable (Python re), not shell."""
import re

# ext -> (public/exported declaration, any function/method declaration, test-file predicate, inline-test-module marker)
LANGS = {
    ".go":  (re.compile(r"^(func (\([^)]*\) )?[A-Z]\w*|type [A-Z]\w*|var [A-Z]\w*|const [A-Z]\w*)"),
             re.compile(r"^func (\([^)]*\) )?(\w+)"),
             lambda p: p.endswith("_test.go"), None),
    ".rs":  (re.compile(r"^\s*pub(\([^)]*\))? (fn|struct|enum|trait|type|const|static|mod) (\w+)"),
             re.compile(r"^\s*(pub(\([^)]*\))? )?((async|const|unsafe) )*fn (\w+)"),
             lambda p: "/tests/" in p or p.endswith("_test.rs") or "/benches/" in p,
             re.compile(r"^\s*#\[cfg\(test\)\]")),
    ".pm":  (re.compile(r"^\s*sub ([a-zA-Z]\w*)"),            # Perl: leading-underscore subs treated as private
             re.compile(r"^\s*sub (\w+)"),
             lambda p: p.endswith(".t") or "/t/" in p or "/tests/" in p, None),
    ".pl":  (re.compile(r"^\s*sub ([a-zA-Z]\w*)"), re.compile(r"^\s*sub (\w+)"),
             lambda p: "/t/" in p or "/tests/" in p, None),
    ".py":  (re.compile(r"^(def [a-zA-Z]\w*|class [A-Z]\w*)"),
             re.compile(r"^\s*(async )?def (\w+)"),
             lambda p: "/tests/" in p or "/test_" in p or p.endswith("_test.py") or "/test/" in p, None),
    ".js":  (re.compile(r"^export (default )?(async )?(function|class|const|let|var)\s*(\w*)"),
             re.compile(r"^\s*(export )?(async )?function\s*(\w+)|^\s*(\w+)\s*\([^)]*\)\s*\{"),
             lambda p: ".test." in p or ".spec." in p or "/__tests__/" in p or "/test/" in p, None),
    ".ts":  (re.compile(r"^export (default )?(async )?(function|class|const|let|var|interface|type|enum)\s*(\w*)"),
             re.compile(r"^\s*(export )?(async )?function\s*(\w+)|^\s*(public |private |protected )?(async )?(\w+)\s*\([^)]*\)\s*[:{]"),
             lambda p: ".test." in p or ".spec." in p or "/__tests__/" in p or "/test/" in p, None),
}
LANGS[".tsx"] = LANGS[".ts"]; LANGS[".jsx"] = LANGS[".js"]

NONPROD_DIRS = re.compile(r"(^|/)(test|tests|testdata|qa|spec|specs|docs?|examples?|bench|benches|website|release|scripts?|tools?|fixtures?|corpus|vendor|node_modules|target|dist|build)/", re.I)


def lang_for(path):
    for ext, spec in LANGS.items():
        if path.endswith(ext):
            return spec
    return None


def is_test(path):
    spec = lang_for(path)
    return bool(NONPROD_DIRS.search(path) or (spec and spec[2](path)))


def split_inline_tests(lines, spec):
    """Return (production_lines, test_lines) for a file with an inline test module marker (Rust)."""
    marker = spec[3]
    if not marker:
        return lines, []
    for i, l in enumerate(lines):
        if marker.match(l):
            return lines[:i], lines[i:]
    return lines, []
