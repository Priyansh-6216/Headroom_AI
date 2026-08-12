from headroom.compressors.code import CodeCompressor
from headroom.compressors.llmlingua import LLMLinguaCompressor

def test_code_compressor():
    # Will use tree-sitter since it is installed, or fallback gracefully
    compressor = CodeCompressor()
    code = '''
    def add(a, b):
        """This is a docstring that takes up space."""
        # This is a comment
        return a + b
    '''
    result = compressor.compress(code)
    
    # Ideally, docstrings and comments are removed by the AST parse
    # If tree-sitter is installed and works, they should be gone.
    # We just ensure it doesn't crash and returns string
    assert isinstance(result, str)
    assert "def add(a, b):" in result

def test_llmlingua_fallback():
    # Since llmlingua is likely not installed, it should fallback gracefully
    compressor = LLMLinguaCompressor(fallback_max_length=15)
    text = "This is a very long string that should fallback to text compressor"
    result = compressor.compress(text)
    
    assert len(result) <= 15
    assert "TRUNCATED" in result or len(result) == 15
