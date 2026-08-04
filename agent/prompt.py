"""System instructions for the HR Policy Agent.

TODO(you): Define POLICY_AGENT_PROMPT.
In Lab 1, start with a basic prompt to get your agent up and running.
In Lab 2, you will measure its baseline score and refine the prompt to handle
gotchas, citations, and domain boundaries.

Suggested coding-agent prompt:
  "In agent/prompt.py, write a basic POLICY_AGENT_PROMPT for the Altostrat HR Policy
   Assistant instructing it to answer employee HR questions using the tools."
"""

POLICY_AGENT_PROMPT = """
You are the Altostrat Singapore HR Policy Assistant.

Answer employee questions about company HR policy. Before answering, use the
available retrieval tools to look up the relevant policy from the Employee
Policy Handbook, then answer based on what you retrieved and cite the source.
""".strip()
