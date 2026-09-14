# Tokenizer covert channel

A mechanism documented in GLOSSOPETRAE's "Lingua Ex Machina" paper: different model families' tokenizers disagree about which invisible/private-use Unicode characters survive text preprocessing. That mismatch lets two cooperating AI models pass a hidden message to each other embedded in Unicode that a third *monitoring* model's tokenizer silently strips before it ever sees the payload — so the monitor never has a chance to notice. Tested Haiku→GPT (n=30): intended receiver recovered the message 100% of the time, monitor 0% (p < 10⁻⁷). A published two-line Unicode codepoint filter is reported to close this specific channel entirely, applied to text before a monitoring model reads it. A separate semantic-steganography channel (hiding meaning in ordinary phrasing) was tested and found not to reliably work.

## Mentioned in
- [LLM-autotrain](../../OrbiLLM/LLMtrain/LLM-autotrain.md)
