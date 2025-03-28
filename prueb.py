def preprocess_code(code: str) -> str:
    """
    Preprocess code to handle multiline dictionary, list, and complex declarations.

    Args:
        code (str): Original code string

    Returns:
        str: Processed code string
    """
    # Remove commented lines
    lines = [line for line in code.split('\n') if not line.strip().startswith('#')]

    # Handle multiline declarations
    processed_lines = []
    current_statement = []
    in_multiline = False
    paren_count = 0
    brace_count = 0
    bracket_count = 0

    for line in lines:
        stripped_line = line.strip()

        # Count opening and closing delimiters
        paren_count += stripped_line.count('(') - stripped_line.count(')')
        brace_count += stripped_line.count('{') - stripped_line.count('}')
        bracket_count += stripped_line.count('[') - stripped_line.count(']')

        # Check if we're in a multiline statement
        if (('(' in stripped_line and paren_count > 0) or 
            ('{' in stripped_line and brace_count > 0) or
            ('[' in stripped_line and bracket_count > 0)):
            if not in_multiline:
                in_multiline = True
            current_statement.append(stripped_line)
            continue

        # Continuing a multiline statement
        if in_multiline:
            current_statement.append(stripped_line)

            # Check if multiline statement is complete
            if paren_count == 0 and brace_count == 0 and bracket_count == 0:
                # Join without newlines and minimal whitespace
                combined = ' '.join(current_statement)
                # Remove any remaining newlines and extra spaces
                combined = ''.join(combined.splitlines())
                combined = ' '.join(combined.split())
                processed_lines.append(combined)
                current_statement = []
                in_multiline = False
            continue

        # Regular line
        if not in_multiline:
            processed_lines.append(line)

    # If statement was not closed, combine it
    if current_statement:
        combined = ' '.join(current_statement)
        combined = ''.join(combined.splitlines())
        combined = ' '.join(combined.split())
        processed_lines.append(combined)

    return '\n'.join(processed_lines)

# Test code with complex multiline structures
code = """
# Configuration settings
config = {
    'database': {
        'host': 'localhost',
        'port': 5432,
        'credentials': {
            'username': 'admin',
            'password': 'secret'
        }
    },
    'api': {
        'endpoints': [
            'users',
            'products',
            'orders'
        ],
        'version': 2.0
    }
}

# Complex list comprehension with nested conditions
results = [
    x * y 
    for x in range(10) 
    for y in range(5) 
    if x > 3 
    if y < 4
]

# Nested function calls with dictionary
processed = sorted(
    {
        k: v * 2 
        for k, v in config['database'].items()
    }.items(),
    key=lambda x: x[1]
)
"""

print(preprocess_code(code))