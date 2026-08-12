from typing import Any
from headroom.core.interfaces import Compressor
from headroom.compressors.text import TextCompressor
from headroom.utils.logger import logger

class CodeCompressor(Compressor):
    """
    Compresses code using tree-sitter AST parsing.
    Removes comments and docstrings to save tokens.
    """
    
    def __init__(self, language: str = "python", max_length: int = 4000):
        self.language = language
        self.max_length = max_length
        self.text_compressor = TextCompressor(max_length=max_length)
        self.parser = None
        self.language_obj = None
        
        self._init_tree_sitter()

    def _init_tree_sitter(self):
        try:
            import tree_sitter
            import tree_sitter_python
            
            self.language_obj = tree_sitter.Language(tree_sitter_python.language())
            self.parser = tree_sitter.Parser(self.language_obj)
        except ImportError:
            logger.warning("tree-sitter or tree-sitter-python not installed. Falling back to text compression.")
            self.parser = None

    def compress(self, data: Any, **kwargs) -> str:
        code = str(data)
        
        if not self.parser or self.language != "python":
            return self.text_compressor.compress(code)
            
        try:
            tree = self.parser.parse(bytes(code, "utf8"))
            root = tree.root_node
            
            # Very simple AST modification: we'll rebuild the string but skip comment nodes
            # To do this robustly we'd need a more complex traversal, but for this demo 
            # we will extract non-comment code blocks
            
            # Since rebuilding from AST is complex, a simple approach is to find all comment
            # and docstring nodes and blank them out.
            
            bytes_code = bytearray(code, "utf8")
            
            def traverse(node):
                # In Python, docstrings are ExpressionStatements containing Strings
                # but standard comments are 'comment' nodes
                if node.type == 'comment':
                    # Replace with spaces to keep line numbers intact (optional)
                    for i in range(node.start_byte, node.end_byte):
                        if bytes_code[i] != 10: # not newline
                            bytes_code[i] = 32 # space
                
                # Check for docstrings (simplification)
                if node.type == 'expression_statement':
                    if len(node.children) == 1 and node.children[0].type == 'string':
                        for i in range(node.start_byte, node.end_byte):
                            if bytes_code[i] != 10:
                                bytes_code[i] = 32
                
                for child in node.children:
                    traverse(child)
                    
            traverse(root)
            
            # Decode and clean up empty lines
            cleaned = bytes_code.decode("utf8")
            lines = [line for line in cleaned.split("\n") if line.strip()]
            final_code = "\n".join(lines)
            
            return self.text_compressor.compress(final_code)
            
        except Exception as e:
            logger.error(f"AST compression failed: {e}. Falling back.")
            return self.text_compressor.compress(code)
