from typing import Any
from headroom.core.interfaces import Compressor
from headroom.compressors.text import TextCompressor
from headroom.utils.logger import logger

class LLMLinguaCompressor(Compressor):
    """
    Compresses text using ML-based LLMLingua-2.
    Requires torch and llmlingua-2 to be installed.
    """
    
    def __init__(self, target_ratio: float = 0.5, fallback_max_length: int = 4000):
        self.target_ratio = target_ratio
        self.fallback = TextCompressor(max_length=fallback_max_length)
        self.compressor_obj = None
        
        self._init_llmlingua()

    def _init_llmlingua(self):
        try:
            from llmlingua import PromptCompressor
            # Use the LLMLingua-2 model for faster compression
            self.compressor_obj = PromptCompressor(
                model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
                use_llmlingua2=True
            )
            logger.info("LLMLingua-2 initialized successfully.")
        except ImportError:
            logger.warning("llmlingua not installed. Use 'pip install headroom-ai[llmlingua]'. Falling back.")
            self.compressor_obj = None
        except Exception as e:
            logger.error(f"Failed to load LLMLingua model: {e}. Falling back.")
            self.compressor_obj = None

    def compress(self, data: Any, **kwargs) -> str:
        text = str(data)
        
        if not self.compressor_obj:
            return self.fallback.compress(text)
            
        try:
            # LLMLingua interface
            results = self.compressor_obj.compress_prompt(
                context=[text],
                instruction="",
                question="",
                target_token=int(len(text.split()) * self.target_ratio)
            )
            return results["compressed_prompt"]
        except Exception as e:
            logger.error(f"LLMLingua compression failed: {e}. Falling back.")
            return self.fallback.compress(text)
