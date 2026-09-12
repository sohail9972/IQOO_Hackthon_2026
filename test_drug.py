from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar  # <-- ADD THIS IMPORT

MODEL_PATH = r"D:\Iqoo_Practice_Project\models\drug-v6-q4_k_m.gguf"
GRAMMAR_PATH = r"D:\Iqoo_Practice_Project\models\coglang.gbnf"
SYSTEM_PATH = r"D:\Iqoo_Practice_Project\models\SYSTEM_v6d.txt"

# Load model
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4,
    verbose=False
)

# Load grammar and system prompt
with open(GRAMMAR_PATH, "r") as f:
    grammar_text = f.read()

with open(SYSTEM_PATH, "r") as f:
    system_prompt = f.read()

# <-- KEY FIX: Wrap the raw GBNF string into a LlamaGrammar object
grammar = LlamaGrammar.from_string(grammar_text)

# Build prompt using the model's expected chat format
prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\nwarfarin interactions<|im_end|>\n<|im_start|>assistant\n"

# Run constrained generation
output = llm.create_completion(
    prompt=prompt,
    grammar=grammar,   # <-- now passing a LlamaGrammar object, not a string
    max_tokens=64,
    temperature=0,
    stop=["<|im_end|>"]
)

print(output['choices'][0]['text'])