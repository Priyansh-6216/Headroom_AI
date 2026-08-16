<div align="center">
  <h1>🧠 Headroom AI</h1>
  <p><b>Intelligent Context Compression & LLM Cost Reduction</b></p>
  <p>Reduce LLM API costs by 50-90% by automatically compressing boilerplate tool outputs, long texts, and massive JSON payloads—while preserving exact system accuracy.</p>
</div>

---

## 📋 Overview

Headroom intercepts and statistically compresses your LLM inputs and tool outputs. When LLM tools fetch data (SQL results, scraped pages, logs), 70-95% of the response is redundant boilerplate. Headroom compresses that away, saving you tokens and lowering latency.

It supports:
- **Smart JSON Compression**: Truncates massive lists but preserves anomalies, exceptions, and the structure.
- **Code AST Compression**: Uses `tree-sitter` to strip comments and docstrings.
- **Framework Integrations**: Out-of-the-box support for `LangChain` and `Agno` agents.
- **Proxy Server**: Run a transparent HTTP proxy that automatically compresses payloads en route to OpenAI/Anthropic.
- **CCR (Compress-Cache-Retrieve)**: Replaces long payloads with memory references, allowing the LLM to recall the original data only if necessary.

## 🚀 Installation

Install Headroom via pip:

```bash
pip install headroom-ai
```

Install with optional framework integrations:

```bash
# For LangChain support
pip install headroom-ai[langchain]

# For Agno support
pip install headroom-ai[agno]

# For the Proxy Server
pip install headroom-ai[proxy]

# For AST Code Compression
pip install headroom-ai[code]
```

## 🛠 Usage & Integrations

### 1. LangChain Integration
Wrap your standard ChatModel to instantly get tool output compression.

```python
from langchain_openai import ChatOpenAI
from headroom.integrations.langchain import HeadroomChatModel

# Wrap any LangChain model
base_model = ChatOpenAI(model="gpt-4o")
llm = HeadroomChatModel(model=base_model)

# Use it just like you normally would!
response = llm.invoke(messages)
```

### 2. Agno Integration
Use `HeadroomAgnoModel` to intercept and compress data right before Agno sends it upstream.

```python
from agno.models.openai import OpenAIChat
from headroom.integrations.agno import HeadroomAgnoModel

# Wrap the Agno model
base_model = OpenAIChat(id="gpt-4o")
agent_model = HeadroomAgnoModel(model=base_model)

response = agent_model.response(messages)
```

### 3. Transparent Proxy Server
If you want zero code changes in your app, route your OpenAI requests through the Headroom proxy server.

1. Start the server:
```bash
python -m headroom.server.proxy
```

2. Point your LLM SDK to the proxy:
```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8787/v1",
    api_key="your-api-key"
)
```

### 4. Raw Compressors
You can use Headroom's internal compressors directly:

```python
from headroom.compressors.smart_crusher import SmartCrusher
from headroom.compressors.code import CodeCompressor

crusher = SmartCrusher(max_list_items=5)
print(crusher.compress([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
# Output: [1, 2, 3, 4, "... [6 more items truncated]"]

code_comp = CodeCompressor()
print(code_comp.compress("def add(a, b):\n    '''This is a docstring'''\n    return a + b"))
# Output: def add(a, b):\n    return a + b
```

## 📊 Benchmarks

Our built-in `Needle In Haystack` test verifies that Headroom safely preserves critical data (like exceptions or errors) while compressing boilerplate.

| Data Type | Original Tokens | Compressed Tokens | Savings |
|-----------|-----------------|-------------------|---------|
| JSON List | 1,601           | 137               | **91.4%** |
| Long Text | 6,501           | 24                | **99.6%** |

## 🤝 Contributing
Contributions are welcome! Please run `pytest` to ensure all tests pass before submitting a PR.
