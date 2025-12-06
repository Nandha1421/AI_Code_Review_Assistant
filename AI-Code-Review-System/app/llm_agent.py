from typing import List
from app.schema import Issue, Severity

def augment_issues_with_suggestions(issues: List[Issue], code: str, language: str) -> List[Issue]:

    out: List[Issue] = []
    for issue in issues:
        from typing import List
        from app.schema import Issue

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            TRANSFORMERS_AVAILABLE = True
        except Exception:
            TRANSFORMERS_AVAILABLE = False

        from app.rag import SimpleRAG


        def _gpt2_generate(prompt: str, max_length: int = 200) -> str:
            if not TRANSFORMERS_AVAILABLE:
                return "(model unavailable) " + prompt[:200]
            tokenizer = AutoTokenizer.from_pretrained("gpt2")
            model = AutoModelForCausalLM.from_pretrained("gpt2")
            gen = pipeline("text-generation", model=model, tokenizer=tokenizer)
            out = gen(prompt, max_length=max_length, do_sample=True, top_p=0.95, temperature=0.8)
            return out[0]["generated_text"] if out else ""


        def augment_issues_with_suggestions(issues: List[Issue], code: str, language: str) -> List[Issue]:
            try:
                rag = SimpleRAG()
                try:
                    rag.add_documents([code], metadatas=[{"source": "current_input"}])
                except Exception:
                    pass

                out: List[Issue] = []
                for issue in issues:
                    # retrieve examples
                    examples = rag.query(issue.message or code, k=3)
                    ctx = "\n---\n".join(examples)
                    prompt = (
                        f"You are an assistant that proposes small code fixes and short explanations.\n"
                        f"Language: {language}\n"
                        f"Code:\n{code}\n\n"
                        f"Issue: {issue.message}\n"
                        f"Relevant examples:\n{ctx}\n"
                        f"Provide a short suggested corrected code snippet and a one-line explanation.\n"
                    )

                    if TRANSFORMERS_AVAILABLE:
                        try:
                            generated = _gpt2_generate(prompt)
                        except Exception:
                            generated = "(generation failed)"
                    else:
                        # fallback deterministic guidance
                        if issue.id == "H-EVAL":
                            generated = (
                                "Avoid eval/exec. Use safe parsing or explicit logic instead.\n"
                                "Example:\nimport ast\nvalue = ast.literal_eval(some_string)"
                            )
                        elif issue.id == "H-SECRET":
                            generated = (
                                "Do not hardcode secrets. Use environment variables.\n"
                                "Example:\nimport os\nAPI_KEY = os.environ.get('MY_API_KEY')"
                            )
                        else:
                            generated = "Suggested fix: review the code and add appropriate handling or refactor."

                    new = Issue(**issue.dict())
                    new.suggested_fix = generated
                    new.explanation = (generated.split("\n")[-1] if generated else "")
                    out.append(new)

                return out
            except Exception:
                return issues
