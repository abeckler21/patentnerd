# openai_prompts.py

PROMPTS = {
    "disambiguate_polysemous_terms": """You are an expert in analyzing patent claim language for polysemous terms that could cause ambiguity. 
Your task is to identify all terms in the given patent text that have multiple potential meanings within the specified domain and suggest a precise, 
context-specific definition for each term. Return only the terms and their clarified definitions, with no additional commentary.

Patent text:
{document}
""",

    "clarify_metaphors": """You are an expert in analyzing metaphorical and figurative language in patents. 
Your task is to identify all metaphorical terms in the given patent text, explain their literal functional meaning in the context of the invention, 
and rewrite them in precise, technical language. Return only the original term, the term’s literal definition, and the rewritten version.

Patent text:
{document}
""",

    "define_collocations": """You are an expert in recognizing and defining domain-specific multi-word expressions in patents. 
Your task is to identify all technical collocations in the provided patent text and provide precise definitions for each as a single unit in the given context, 
avoiding definitions of individual words. Return only the collocation and its definition.

Patent text:
{document}
""",

    "control_scope_ambiguity": """You are an expert in detecting scope ambiguity in patent language. 
Your task is to identify vague or overbroad terms in the given patent text (quantifiers include “any,” “arbitrary,” “dynamic,” “automatic”, etc…) 
and rewrite them with specific boundaries and limitations based on the context of the invention. 
Return only the original term and its more precise version.

Patent text:
{document}
""",

    "enforce_controlled_vocabulary": """You are an expert in ensuring consistent terminology in patent drafting. 
Your task is to identify cases in the given patent text where different terms are used for the same concept, the same term is defined with different meanings, 
or where similar yet distinct concepts are combined. Replace them with a single, consistent term that best reflects the intended meaning. 
Return only the inconsistent terms and their standardized replacement.

Patent text:
{document}
"""
}
