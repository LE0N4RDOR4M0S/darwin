from transformers import AutoTokenizer, AutoModelForCausalLM

class TinyLlamaAdapter:
    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def suggest_patch(self, code_snippet: str, issue: str) -> str:
        prompt = f"O código abaixo apresenta o problema: {issue}\n. Sugira uma correção:\n\n{code_snippet}"
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=100)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
