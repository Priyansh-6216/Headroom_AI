from headroom.compressors.text import TextCompressor

def test_text_compressor_no_truncation():
    compressor = TextCompressor(max_length=50)
    text = "Short text"
    assert compressor.compress(text) == text

def test_text_compressor_truncation():
    compressor = TextCompressor(max_length=20, suffix="... [TRUNC]")
    text = "This is a very long text that should be truncated"
    result = compressor.compress(text)
    assert len(result) == 20
    assert result.endswith("... [TRUNC]")
    assert result == "This is a... [TRUNC]"
