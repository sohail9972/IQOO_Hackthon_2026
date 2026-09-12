from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar

# ============================================================
# CONFIGURATION
# ============================================================
MODEL_PATH = r"D:\Iqoo_Practice_Project\models\drug-v6-q4_k_m.gguf"
GRAMMAR_PATH = r"D:\Iqoo_Practice_Project\models\coglang.gbnf"
SYSTEM_PATH = r"D:\Iqoo_Practice_Project\models\SYSTEM_v6d.txt"

# ============================================================
# LOAD MODEL
# ============================================================
print("Loading model... (this may take a few seconds)")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4,
    verbose=False
)
print("Model loaded.\n")

# ============================================================
# LOAD GRAMMAR AND SYSTEM PROMPT
# ============================================================
grammar = LlamaGrammar.from_file(GRAMMAR_PATH)

with open(SYSTEM_PATH, "r", encoding="utf-8") as f:
    system_prompt = f.read()

# ============================================================
# TEST PROMPTS
# ============================================================
test_prompts = [
    "warfarin interactions",
    "list the adverse effects caused by ibuprofen",
    "list the populations for which naproxen is contraindicated",
    "for each drug in warfarin, aspirin, return its name",
    "audit an update that sets aspirin name",
    "list what ibuprofen causes",
    "show what warfarin interacts with",
    "find the conditions for which metformin is contraindicated",
]

# ============================================================
# RUN INFERENCE FOR EACH PROMPT
# ============================================================
print("=" * 60)
print("COGLANG MEDICATION QUERY TRANSLATION TEST")
print("=" * 60)

for i, user_input in enumerate(test_prompts, 1):
    prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_input}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    output = llm.create_completion(
        prompt=prompt,
        grammar=grammar,
        max_tokens=64,
        temperature=0,
        stop=["<|im_end|>"]
    )

    result = output['choices'][0]['text'].strip()

    print(f"\n[{i}] INPUT : {user_input}")
    print(f"    OUTPUT: {result}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)