import difflib
import tokenize
from io import BytesIO
from fuzzywuzzy import fuzz


def read_code(file_path):
    """Read code content from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def line_similarity(line1, line2, threshold=0.8):
    """Compare two lines for similarity using Levenshtein ratio."""
    similarity_ratio = difflib.SequenceMatcher(None, line1, line2).ratio()
    return similarity_ratio >= threshold


def compare_code_lines(code1, code2, threshold=0.8):
    """Compare two code snippets line by line and highlight similarities."""
    code1_lines = code1.splitlines()
    code2_lines = code2.splitlines()

    similar_lines = []
    for i, line1 in enumerate(code1_lines, start=1):
        for j, line2 in enumerate(code2_lines, start=1):
            similarity_ratio = difflib.SequenceMatcher(None, line1, line2).ratio()
            if similarity_ratio >= threshold:
                similar_lines.append({
                    "file1_line": i,
                    "file2_line": j,
                    "file1_content": line1.strip(),
                    "file2_content": line2.strip(),
                    "similarity": similarity_ratio
                })
    return similar_lines



def extract_functions(code):
    """Extract function definitions from Python code."""
    functions = []
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):  # Function signature
            function_body = []
            indentation = len(line) - len(line.lstrip())
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                next_indentation = len(next_line) - len(next_line.lstrip())
                if next_line.strip() and next_indentation > indentation:
                    function_body.append(next_line.strip())
                else:
                    break
            functions.append({
                "signature": line.strip(),
                "body": "\n".join(function_body),
                "line_number": i + 1
            })
    return functions


def compare_functions(file1, file2, threshold=75):
    """Compare functions from two files for similarity."""
    code1 = read_code(file1)
    code2 = read_code(file2)

    functions1 = extract_functions(code1)
    functions2 = extract_functions(code2)

    similar_functions = []
    for func1 in functions1:
        for func2 in functions2:
            signature_similarity = fuzz.ratio(func1["signature"], func2["signature"])
            body_similarity = fuzz.ratio(func1["body"], func2["body"])
            if signature_similarity > threshold or body_similarity > threshold:
                similar_functions.append({
                    "file1_function": func1["signature"],
                    "file1_line": func1["line_number"],
                    "file2_function": func2["signature"],
                    "file2_line": func2["line_number"],
                    "signature_similarity": signature_similarity,
                    "body_similarity": body_similarity,
                })
    return similar_functions


def calculate_similarity(file1, file2):
    """Calculate similarity scores and detect similar code."""
    code1 = read_code(file1)
    code2 = read_code(file2)

    tokens1 = tokenize_code(code1)
    tokens2 = tokenize_code(code2)

    string_similarity = difflib.SequenceMatcher(None, code1, code2).ratio()
    token_similarity = jaccard_similarity(tokens1, tokens2)

    diff_lines = compare_code_lines(code1, code2, threshold=0.8)
    similar_funcs = compare_functions(file1, file2)

    return {
        "string_similarity": string_similarity,
        "token_similarity": token_similarity,
        "diff_lines": diff_lines,
        "similar_functions": similar_funcs,
    }


def tokenize_code(code):
    """Tokenize Python code into a list of tokens."""
    tokens = []
    try:
        for token in tokenize.tokenize(BytesIO(code.encode('utf-8')).readline):
            tokens.append(token.string)
    except tokenize.TokenError:
        pass
    return tokens


def jaccard_similarity(tokens1, tokens2):
    """Calculate Jaccard similarity between two sets of tokens."""
    set1 = set(tokens1)
    set2 = set(tokens2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union
