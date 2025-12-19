"""Voice analysis using LLM."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

import httpx

from .config import Config

# Analysis prompt that extracts voice patterns
ANALYSIS_PROMPT = """You are an expert communication analyst. Analyze the following writing samples and extract a comprehensive voice profile.

The samples come from the same person. Your job is to identify:
1. Core voice characteristics (the defining tensions/qualities)
2. Vocabulary patterns (signature phrases, preferred words, avoided words)
3. Structural patterns (how they organize information)
4. Tone spectrum (how formality varies by context)
5. Do/Don't patterns (explicit preferences)
6. Example templates for common communication types

Return your analysis as COMPACT JSON (no line breaks within string values) with this exact structure:

```json
{
  "core_dna": {
    "primary_qualities": ["quality1 - explanation", "quality2 - explanation"],
    "defining_tensions": ["tension1: description", "tension2: description"]
  },
  "vocabulary": {
    "signature_phrases": {
      "acknowledgments": ["phrase1", "phrase2"],
      "confirmations": ["phrase1", "phrase2"],
      "transitions": ["phrase1", "phrase2"],
      "emphasis": ["phrase1", "phrase2"]
    },
    "preferred_words": ["word1", "word2"],
    "avoided_words": ["word1", "word2"],
    "banned_phrases": ["phrase1", "phrase2"]
  },
  "structure": {
    "paragraph_style": "description of typical paragraph length and flow",
    "list_usage": "when bullets vs prose",
    "opening_patterns": ["pattern1", "pattern2"],
    "closing_patterns": ["pattern1", "pattern2"],
    "common_templates": [
      {
        "type": "email_status_update",
        "template": "template text with [placeholders]"
      }
    ]
  },
  "tone_spectrum": {
    "casual": "description of casual tone (slack/teams)",
    "professional": "description of professional tone (emails)",
    "formal": "description of formal tone (exec/external)"
  },
  "do_patterns": ["pattern1", "pattern2"],
  "dont_patterns": ["pattern1", "pattern2"],
  "formatting": {
    "preferences": ["pref1", "pref2"],
    "avoid": ["avoid1", "avoid2"]
  },
  "long_form": {
    "typical_length": "word count range",
    "characteristics": ["char1", "char2"]
  }
}
```

Be specific and grounded in the actual samples. Use exact phrases from the samples as evidence. If a pattern isn't clearly present, omit it rather than inventing.

---

WRITING SAMPLES:

"""


@dataclass
class VoiceAnalysisResult:
    """Result of voice analysis."""

    raw_response: str
    parsed: dict | None
    error: str | None = None


def collect_samples(samples_path: Path) -> dict[str, list[str]]:
    """
    Collect writing samples from the samples directory.

    Returns dict mapping category to list of sample contents.
    """
    samples = {}

    if not samples_path.exists():
        return samples

    # Check for category subdirectories
    for item in samples_path.iterdir():
        if item.is_dir():
            category = item.name
            samples[category] = []
            for file in item.glob("*"):
                if file.is_file() and file.suffix in (".md", ".txt", ".eml", ""):
                    try:
                        content = file.read_text(errors="ignore")
                        if content.strip():
                            samples[category].append(content)
                    except Exception:
                        pass
        elif item.is_file() and item.suffix in (".md", ".txt", ".eml", ""):
            # Files directly in samples/ go to "general"
            if "general" not in samples:
                samples["general"] = []
            try:
                content = item.read_text(errors="ignore")
                if content.strip():
                    samples["general"].append(content)
            except Exception:
                pass

    return samples


def build_prompt(samples: dict[str, list[str]]) -> str:
    """Build the full analysis prompt with samples."""
    prompt = ANALYSIS_PROMPT

    for category, contents in samples.items():
        prompt += f"\n## {category.upper()} SAMPLES\n\n"
        for i, content in enumerate(contents, 1):
            # Truncate very long samples
            if len(content) > 5000:
                content = content[:5000] + "\n[... truncated ...]"
            prompt += f"### Sample {i}\n```\n{content}\n```\n\n"

    return prompt


def call_openrouter(
    prompt: str,
    api_key: str,
    model: str = "google/gemini-3-flash-preview",
    max_tokens: int = 8000,
) -> str:
    """Call OpenRouter API with the analysis prompt."""
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/BioInfo/continuum",
        "X-Title": "Continuum Voice Analysis",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,  # Lower temperature for more consistent analysis
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]


def fix_broken_json_strings(json_str: str) -> str:
    """Fix JSON that has line breaks inside string values."""
    import re

    # Find all strings and fix newlines within them
    result = []
    in_string = False
    escape_next = False
    i = 0

    while i < len(json_str):
        char = json_str[i]

        if escape_next:
            result.append(char)
            escape_next = False
        elif char == '\\':
            result.append(char)
            escape_next = True
        elif char == '"':
            result.append(char)
            in_string = not in_string
        elif char == '\n' and in_string:
            # Replace newline inside string with space
            result.append(' ')
        else:
            result.append(char)

        i += 1

    return ''.join(result)


def parse_analysis(response: str) -> dict | None:
    """Parse the JSON analysis from the response."""
    import re

    def try_parse(json_str: str) -> dict | None:
        """Try to parse JSON, with fallback to fixing broken strings."""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try fixing broken strings
            fixed = fix_broken_json_strings(json_str)
            try:
                return json.loads(fixed)
            except:
                return None

    # Try to find JSON between ```json and ```
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
    if json_match:
        result = try_parse(json_match.group(1).strip())
        if result:
            return result

    # Try finding any ``` block
    code_match = re.search(r'```\s*([\s\S]*?)\s*```', response)
    if code_match:
        result = try_parse(code_match.group(1).strip())
        if result:
            return result

    # Try parsing from first { to last }
    start = response.find('{')
    end = response.rfind('}')
    if start != -1 and end != -1:
        result = try_parse(response[start:end+1])
        if result:
            return result

    return None


def generate_voice_md(analysis: dict) -> str:
    """Generate voice.md content from analysis."""
    lines = ["# Voice Profile", "", ""]

    # Core DNA
    if "core_dna" in analysis:
        lines.append("## Core DNA")
        lines.append("")
        if "defining_tensions" in analysis["core_dna"]:
            for tension in analysis["core_dna"]["defining_tensions"]:
                lines.append(f"**{tension}**")
                lines.append("")
        if "primary_qualities" in analysis["core_dna"]:
            for quality in analysis["core_dna"]["primary_qualities"]:
                lines.append(f"- {quality}")
            lines.append("")

    # Tone Spectrum
    if "tone_spectrum" in analysis:
        lines.append("## Tone Spectrum")
        lines.append("")
        ts = analysis["tone_spectrum"]
        if "casual" in ts:
            lines.append(f"- **Casual (Teams/Slack)**: {ts['casual']}")
        if "professional" in ts:
            lines.append(f"- **Professional (Email)**: {ts['professional']}")
        if "formal" in ts:
            lines.append(f"- **Formal (Exec/External)**: {ts['formal']}")
        lines.append("")

    # Do patterns
    if "do_patterns" in analysis and analysis["do_patterns"]:
        lines.append("## Do")
        lines.append("")
        for pattern in analysis["do_patterns"]:
            lines.append(f"- {pattern}")
        lines.append("")

    # Don't patterns
    if "dont_patterns" in analysis and analysis["dont_patterns"]:
        lines.append("## Don't")
        lines.append("")
        for pattern in analysis["dont_patterns"]:
            lines.append(f"- {pattern}")
        lines.append("")

    # Vocabulary
    if "vocabulary" in analysis:
        lines.append("## Vocabulary")
        lines.append("")
        vocab = analysis["vocabulary"]

        if "signature_phrases" in vocab:
            lines.append("### Signature Phrases")
            lines.append("")
            for category, phrases in vocab["signature_phrases"].items():
                if phrases:
                    lines.append(
                        f"- **{category.title()}**: {', '.join(f'\"{p}\"' for p in phrases)}"
                    )
            lines.append("")

        if "avoided_words" in vocab or "banned_phrases" in vocab:
            lines.append("### Avoid")
            lines.append("")
            for word in vocab.get("avoided_words", []):
                lines.append(f"- {word}")
            for phrase in vocab.get("banned_phrases", []):
                lines.append(f"- \"{phrase}\"")
            lines.append("")

    # Structure
    if "structure" in analysis:
        lines.append("## Structural Patterns")
        lines.append("")
        struct = analysis["structure"]

        if "paragraph_style" in struct:
            lines.append(f"**Paragraph style**: {struct['paragraph_style']}")
            lines.append("")
        if "list_usage" in struct:
            lines.append(f"**List usage**: {struct['list_usage']}")
            lines.append("")

        if "common_templates" in struct:
            for template in struct["common_templates"]:
                lines.append(f"**{template.get('type', 'Template')}**:")
                lines.append("```")
                lines.append(template.get("template", ""))
                lines.append("```")
                lines.append("")

    # Formatting
    if "formatting" in analysis:
        lines.append("## Formatting")
        lines.append("")
        fmt = analysis["formatting"]
        if "preferences" in fmt:
            for pref in fmt["preferences"]:
                lines.append(f"- {pref}")
        lines.append("")

    # Long-form
    if "long_form" in analysis:
        lines.append("## Long-Form Writing")
        lines.append("")
        lf = analysis["long_form"]
        if "typical_length" in lf:
            lines.append(f"**Typical length**: {lf['typical_length']}")
        if "characteristics" in lf:
            lines.append("")
            for char in lf["characteristics"]:
                lines.append(f"- {char}")
        lines.append("")

    return "\n".join(lines)


def analyze_voice(
    config: Config,
    samples_path: Path | None = None,
    api_key: str | None = None,
    model: str = "google/gemini-3-flash-preview",
) -> VoiceAnalysisResult:
    """
    Analyze writing samples and generate voice profile.

    Args:
        config: Continuum configuration
        samples_path: Path to samples directory (default: ~/.continuum/samples)
        api_key: OpenRouter API key (default: from env OPENROUTER_API_KEY)
        model: Model to use for analysis

    Returns:
        VoiceAnalysisResult with the analysis
    """
    # Get samples path
    if samples_path is None:
        samples_path = config.base_path / "samples"

    # Get API key
    if api_key is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            return VoiceAnalysisResult(
                raw_response="",
                parsed=None,
                error="OPENROUTER_API_KEY environment variable not set",
            )

    # Collect samples
    samples = collect_samples(samples_path)
    if not samples:
        return VoiceAnalysisResult(
            raw_response="",
            parsed=None,
            error=f"No samples found in {samples_path}. Add .md or .txt files to analyze.",
        )

    # Count samples
    total_samples = sum(len(v) for v in samples.values())

    # Build prompt
    prompt = build_prompt(samples)

    # Call API
    try:
        response = call_openrouter(prompt, api_key, model)
    except httpx.HTTPStatusError as e:
        return VoiceAnalysisResult(
            raw_response="",
            parsed=None,
            error=f"API error: {e.response.status_code} - {e.response.text}",
        )
    except Exception as e:
        return VoiceAnalysisResult(
            raw_response="", parsed=None, error=f"Error calling API: {e}"
        )

    # Parse response
    parsed = parse_analysis(response)

    return VoiceAnalysisResult(raw_response=response, parsed=parsed, error=None)
