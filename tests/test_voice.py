"""Tests for voice module."""

import pytest
from pathlib import Path

from continuum.voice import (
    parse_analysis,
    collect_samples,
    generate_voice_md,
)
from continuum.cli import auto_detect_category


class TestParseAnalysis:
    """Tests for parse_analysis()."""

    def test_parses_json_code_block(self):
        response = '```json\n{"core_dna": {"primary_qualities": ["clear"]}}\n```'
        result = parse_analysis(response)
        assert result is not None
        assert result["core_dna"]["primary_qualities"] == ["clear"]

    def test_parses_plain_code_block(self):
        response = '```\n{"core_dna": {"primary_qualities": ["clear"]}}\n```'
        result = parse_analysis(response)
        assert result is not None
        assert "core_dna" in result

    def test_parses_raw_json(self):
        response = 'Here is the analysis:\n{"core_dna": {"primary_qualities": ["clear"]}}\nEnd.'
        result = parse_analysis(response)
        assert result is not None
        assert "core_dna" in result

    def test_handles_broken_json_strings(self):
        # JSON with newlines inside string values
        response = '```json\n{"core_dna": {"primary_qualities": ["clear\nand direct"]}}\n```'
        result = parse_analysis(response)
        assert result is not None
        assert "core_dna" in result

    def test_returns_none_for_no_json(self):
        response = "This is just text with no JSON at all."
        result = parse_analysis(response)
        assert result is None

    def test_returns_none_for_invalid_json(self):
        response = '```json\n{invalid json here}\n```'
        result = parse_analysis(response)
        assert result is None


class TestCollectSamples:
    """Tests for collect_samples()."""

    def test_collects_from_subdirectories(self, tmp_path):
        emails = tmp_path / "emails"
        emails.mkdir()
        (emails / "sample1.md").write_text("Hello, this is a sample email.")
        (emails / "sample2.txt").write_text("Another email sample.")

        result = collect_samples(tmp_path)
        assert "emails" in result
        assert len(result["emails"]) == 2

    def test_collects_from_root_as_general(self, tmp_path):
        (tmp_path / "sample.md").write_text("A general sample.")

        result = collect_samples(tmp_path)
        assert "general" in result
        assert len(result["general"]) == 1

    def test_skips_unsupported_extensions(self, tmp_path):
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "valid.md").write_text("Valid sample")

        result = collect_samples(tmp_path)
        assert "general" in result
        assert len(result["general"]) == 1

    def test_empty_directory(self, tmp_path):
        empty = tmp_path / "empty_samples"
        empty.mkdir()

        result = collect_samples(empty)
        assert result == {}

    def test_nonexistent_directory(self, tmp_path):
        result = collect_samples(tmp_path / "nonexistent")
        assert result == {}

    def test_skips_empty_files(self, tmp_path):
        (tmp_path / "empty.md").write_text("")
        (tmp_path / "whitespace.md").write_text("   \n  \n  ")
        (tmp_path / "valid.md").write_text("Valid content")

        result = collect_samples(tmp_path)
        assert "general" in result
        assert len(result["general"]) == 1


class TestAutoDetectCategory:
    """Tests for auto_detect_category() edge cases."""

    def test_case_insensitive(self):
        assert auto_detect_category("DECIDED to use Python") == "decision"
        assert auto_detect_category("LEARNED a new trick") == "lesson"

    def test_partial_match_in_word(self):
        # "always" is a preference keyword
        assert auto_detect_category("I always use type hints") == "preference"

    def test_empty_string(self):
        assert auto_detect_category("") == "fact"


class TestGenerateVoiceMd:
    """Tests for generate_voice_md()."""

    def test_basic_structure(self):
        analysis = {
            "core_dna": {
                "primary_qualities": ["Direct", "Technical"],
                "defining_tensions": ["Brevity vs completeness"],
            },
            "tone_spectrum": {
                "casual": "Short, direct",
                "professional": "Structured, clear",
                "formal": "Precise, measured",
            },
            "do_patterns": ["Use concrete examples", "Lead with the point"],
            "dont_patterns": ["Use filler words", "Over-qualify statements"],
        }
        result = generate_voice_md(analysis)

        assert "# Voice Profile" in result
        assert "## Core DNA" in result
        assert "## Tone Spectrum" in result
        assert "## Do" in result
        assert "## Don't" in result
        assert "Direct" in result
        assert "Use concrete examples" in result

    def test_handles_empty_analysis(self):
        result = generate_voice_md({})
        assert "# Voice Profile" in result

    def test_handles_partial_analysis(self):
        analysis = {
            "core_dna": {
                "primary_qualities": ["Clear"],
            }
        }
        result = generate_voice_md(analysis)
        assert "# Voice Profile" in result
        assert "Clear" in result

    def test_vocabulary_section(self):
        analysis = {
            "vocabulary": {
                "signature_phrases": {
                    "acknowledgments": ["Got it", "Makes sense"],
                },
                "avoided_words": ["synergy"],
                "banned_phrases": ["let's circle back"],
            }
        }
        result = generate_voice_md(analysis)
        assert "## Vocabulary" in result
        assert "Got it" in result
        assert "synergy" in result
        assert "circle back" in result
