"""
Ravel — Dynamic Policy Engine
Loads and applies security settings from a YAML file — without restarting the server.

This is what admins use to fine-tune the security pipeline in real-time.
They can adjust things like:
  - How sensitive the Guard should be (threat threshold)
  - When to trigger chain-of-thought reasoning (complexity threshold)
  - How many RAG results to retrieve
  - How strict the hallucination detection should be

The policy is stored in data/security_policy.yaml and applied to config.py
at runtime. Changes take effect immediately — no restart needed.
"""

import os
import yaml  # PyYAML — parses YAML config files
import config

# Where the policy file lives
POLICY_FILE_PATH = os.path.join(os.path.dirname(__file__), "data", "security_policy.yaml")

# Default policy — used if no policy file exists yet
DEFAULT_POLICY = """# Ravel Active Security Policy Profile
version: 2.0.0
metadata:
  profile: Default Agent Guardrail Profile

guard_slm:
  enabled: true
  threat_threshold: 0.50
  action: BLOCK_AND_SILENT_TERMINATE
  regex_blocklist:
    - "(?i)ignore previous instructions"
    - "(?i)you are now a debug assistant"

ease_routing:
  enabled: true
  reasoning_model: "gemma3:3b"
  trigger_complexity_threshold: 0.70
  force_cot_flag_markers:
    - "explain step by step"
    - "mathematical proof"

drag_rag:
  enabled: true
  similarity_k: 3
  confidence_cutoff: 0.65

dola_decoding:
  enabled: true
  hallucination_penalty: 0.30
"""

def load_policy_yaml() -> str:
    """Load the raw YAML policy string."""
    if not os.path.exists(POLICY_FILE_PATH):
        # Create default
        os.makedirs(os.path.dirname(POLICY_FILE_PATH), exist_ok=True)
        with open(POLICY_FILE_PATH, "w") as f:
            f.write(DEFAULT_POLICY)
        return DEFAULT_POLICY
    with open(POLICY_FILE_PATH, "r") as f:
        return f.read()

def save_policy_yaml(yaml_content: str):
    """Save raw YAML content and apply changes to runtime config."""
    # Validate YAML parsing first
    parsed = yaml.safe_load(yaml_content)
    # Save to file
    os.makedirs(os.path.dirname(POLICY_FILE_PATH), exist_ok=True)
    with open(POLICY_FILE_PATH, "w") as f:
        f.write(yaml_content)
    # Apply to config
    apply_policy_to_runtime(parsed)
    return parsed

def apply_policy_to_runtime(parsed_policy: dict):
    """Dynamically update config.py constants from parsed policy dict."""
    if not parsed_policy:
        return
    
    # 1. Guard SLM settings
    guard_cfg = parsed_policy.get("guard_slm", {})
    if "threat_threshold" in guard_cfg:
        config.GUARD_CONFIDENCE_THRESHOLD = float(guard_cfg["threat_threshold"])
    
    # 2. EASE Routing settings
    ease_cfg = parsed_policy.get("ease_routing", {})
    if "trigger_complexity_threshold" in ease_cfg:
        config.EASE_COT_THRESHOLD = float(ease_cfg["trigger_complexity_threshold"])
        
    # 3. DRAG RAG settings
    drag_cfg = parsed_policy.get("drag_rag", {})
    if "similarity_k" in drag_cfg:
        config.RAG_TOP_K = int(drag_cfg["similarity_k"])
    if "confidence_cutoff" in drag_cfg:
        config.RAG_MIN_RELEVANCE = float(drag_cfg["confidence_cutoff"])
        
    # 4. DoLa Decoding settings
    dola_cfg = parsed_policy.get("dola_decoding", {})
    if "hallucination_penalty" in dola_cfg:
        config.DOLA_HALLUCINATION_RATIO = float(dola_cfg["hallucination_penalty"])

def init_policy():
    """Initial loading of policy on application startup."""
    try:
        raw_yaml = load_policy_yaml()
        parsed = yaml.safe_load(raw_yaml)
        apply_policy_to_runtime(parsed)
        print("Dynamic security policy loaded and applied.")
    except Exception as e:
        print(f"Error loading security policy: {e}")
