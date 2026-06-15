"""
Align Whisper transcript to manuscript for calibrated sentence segmentation.

Replaces gen_analysis.js when a manuscript is available. Uses the manuscript
as ground truth for text content and sentence structure, while keeping
Whisper timestamps for timing.

Auto-detects manuscript files in scripts/ directory.
If multiple files found, asks user to choose.

Usage:
    python align_to_manuscript.py <video_project_dir> <subtitles_words.json> <output_dir>

Example:
    python align_to_manuscript.py \
        "D:\work\OPC\videos\把8个AI Agent塞进明代朝廷，我当了回朱元璋" \
        "Rough\review\OBS\1_转录\subtitles_words.json" \
        "Rough\review\OBS\2_分析"
"""
import json
import re
import sys
import difflib
from pathlib import Path
from typing import List, Tuple, Optional


# ─── Manuscript parsing ───────────────────────────────────────────────

def find_manuscripts(video_dir: Path) -> List[Path]:
    """Auto-detect manuscript .md files in scripts/ directory."""
    scripts_dir = video_dir / "scripts"
    if not scripts_dir.is_dir():
        return []
    md_files = sorted(scripts_dir.glob("*.md"))
    # Filter out obvious non-manuscript files (README, templates, etc.)
    return [f for f in md_files if not f.name.startswith("README") and not f.name.startswith("template")]


def ask_user_manuscript(manuscripts: List[Path], choice: int = 0) -> Path:
    """Ask user to choose when multiple manuscripts found.
    
    Args:
        manuscripts: List of manuscript paths
        choice: If >0, use 1-based index directly (non-interactive mode)
    """
    if len(manuscripts) == 1:
        return manuscripts[0]
    if choice > 0 and choice <= len(manuscripts):
        return manuscripts[choice - 1]
    # Interactive mode
    print(f"\n找到 {len(manuscripts)} 个文稿文件：")
    for i, f in enumerate(manuscripts):
        print(f"  [{i + 1}] {f.name}")
    while True:
        user_input = input(f"\n选择文稿编号 (1-{len(manuscripts)}): ").strip()
        if user_input.isdigit() and 1 <= int(user_input) <= len(manuscripts):
            return manuscripts[int(user_input) - 1]


def parse_manuscript(manuscript_path: Path) -> List[dict]:
    """
    Parse manuscript markdown into spoken sentences.
    
    Extracts ONLY spoken text, skipping:
    - Section headers (# ...)
    - Visual cues 【画面：...】 【字幕卡：...】
    - Markdown formatting (**bold**, //, etc.)
    - Empty lines
    
    Returns list of {text, section, sentence_idx} dicts.
    """
    content = manuscript_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    sentences = []
    current_section = ""
    raw_text_buffer = ""
    
    for line in lines:
        stripped = line.strip()
        
        # Section header
        if stripped.startswith("#"):
            current_section = stripped.lstrip("#").strip()
            continue
        
        # Skip visual cues
        if stripped.startswith("【") or stripped.startswith("---"):
            continue
        
        # Skip empty lines (but flush buffer on empty)
        if not stripped:
            if raw_text_buffer:
                _flush_sentences(sentences, raw_text_buffer, current_section)
                raw_text_buffer = ""
            continue
        
        # Remove bold markers
        cleaned = re.sub(r"\*\*", "", stripped)
        # Remove pause markers
        cleaned = cleaned.replace("//", "")
        
        raw_text_buffer += cleaned
    
    # Flush remaining
    if raw_text_buffer:
        _flush_sentences(sentences, raw_text_buffer, current_section)
    
    return sentences


def _flush_sentences(sentences: list, text: str, section: str):
    """Split accumulated text into sentences by Chinese punctuation."""
    # Split by sentence-ending punctuation, keep the punctuation
    parts = re.split(r"(?<=[。！？])", text)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Further split by commas if the segment is very long (>80 chars)
        if len(part) > 80:
            sub_parts = re.split(r"(?<=[，；])", part)
            for sp in sub_parts:
                sp = sp.strip()
                if sp:
                    sentences.append({
                        "text": sp,
                        "section": section,
                        "idx": len(sentences),
                    })
        else:
            sentences.append({
                "text": part,
                "section": section,
                "idx": len(sentences),
            })


# ─── Whisper flattening ───────────────────────────────────────────────

def flatten_whisper(words: List[dict]) -> Tuple[str, List[Tuple[int, int, float, float]]]:
    """
    Flatten Whisper words into a character sequence with back-references.
    
    Returns:
        (normalized_text, char_map)
        where char_map[i] = (word_index, char_pos_in_word, start_time, end_time)
    """
    chars = []
    char_map = []
    
    for w_idx, w in enumerate(words):
        if w.get("isGap"):
            continue
        text = w.get("text", "")
        start = w.get("start", 0)
        end = w.get("end", 0)
        for c_idx, c in enumerate(text):
            normalized = _normalize_char(c)
            if normalized:
                chars.append(normalized)
                char_map.append((w_idx, c_idx, start, end))
    
    return "".join(chars), char_map


def _normalize_char(c: str) -> str:
    """Normalize a character for matching. Returns empty string to skip."""
    # Skip whitespace
    if c.isspace():
        return ""
    # Skip punctuation
    if c in "，。！？、；：""''（）《》【】""''…—·.,!?;:\"'()[]{}/":
        return ""
    # Keep everything else
    return c


# ─── Alignment ────────────────────────────────────────────────────────

def align_manuscript_to_whisper(
    manuscript_sentences: List[dict],
    whisper_chars: str,
    char_map: List[Tuple[int, int, float, float]],
) -> List[dict]:
    """
    Align each manuscript sentence to a range of Whisper word indices.
    
    Uses difflib.SequenceMatcher for character-level alignment.
    Handles ASR errors (substitutions), ad-libs (insertions), and skips (deletions).
    
    Returns manuscript_sentences with added fields:
        - startIdx: first Whisper word index
        - endIdx: last Whisper word index
        - start_time: sentence start time
        - end_time: sentence end time
        - confidence: alignment confidence (0-1)
        - matched: whether a match was found
    """
    # Build manuscript character sequence
    ms_chars = ""
    ms_sentence_ranges = []  # (start_char, end_char) for each sentence
    for sent in manuscript_sentences:
        start_char = len(ms_chars)
        for c in sent["text"]:
            normalized = _normalize_char(c)
            if normalized:
                ms_chars += normalized
        end_char = len(ms_chars)
        ms_sentence_ranges.append((start_char, end_char))
    
    # Run SequenceMatcher
    matcher = difflib.SequenceMatcher(None, ms_chars, whisper_chars, autojunk=False)
    
    # Build mapping: manuscript char index → whisper char index
    ms_to_whisper = {}  # ms_char_idx → whisper_char_idx
    for block in matcher.get_matching_blocks():
        ms_start, wh_start, length = block
        for i in range(length):
            ms_to_whisper[ms_start + i] = wh_start + i
    
    # For each sentence, find the word index range
    for sent_idx, (ms_start, ms_end) in enumerate(ms_sentence_ranges):
        sent = manuscript_sentences[sent_idx]
        
        # Find whisper char indices for this sentence's chars
        wh_char_indices = []
        for ms_c in range(ms_start, ms_end):
            if ms_c in ms_to_whisper:
                wh_char_indices.append(ms_to_whisper[ms_c])
        
        if not wh_char_indices:
            # No match found — this sentence wasn't spoken or alignment failed
            sent["startIdx"] = -1
            sent["endIdx"] = -1
            sent["start_time"] = 0
            sent["end_time"] = 0
            sent["confidence"] = 0.0
            sent["matched"] = False
            continue
        
        # Map whisper char indices to word indices
        wh_first = wh_char_indices[0]
        wh_last = wh_char_indices[-1]
        word_start = char_map[wh_first][0]  # word index of first matched char
        word_end = char_map[wh_last][0]     # word index of last matched char
        
        # Times
        start_time = char_map[wh_first][2]
        end_time = char_map[wh_last][3]
        
        # Confidence = matched chars / total sentence chars
        total_chars = ms_end - ms_start
        matched_chars = len(wh_char_indices)
        confidence = matched_chars / total_chars if total_chars > 0 else 0
        
        sent["startIdx"] = word_start
        sent["endIdx"] = word_end
        sent["start_time"] = start_time
        sent["end_time"] = end_time
        sent["confidence"] = round(confidence, 3)
        sent["matched"] = True
    
    return manuscript_sentences


# ─── Output generation ────────────────────────────────────────────────

def generate_outputs(
    aligned_sentences: List[dict],
    words: List[dict],
    output_dir: Path,
):
    """Generate analysis.txt, sentence_map.json, auto_selected.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Filter to matched sentences only
    matched = [s for s in aligned_sentences if s.get("matched")]
    unmatched = [s for s in aligned_sentences if not s.get("matched")]
    
    # analysis.txt: manuscript text (corrected)
    lines = []
    for i, sent in enumerate(matched):
        lines.append(f"{i}: {sent['text']}")
    (output_dir / "analysis.txt").write_text("\n".join(lines), encoding="utf-8")
    
    # sentence_map.json: word index ranges
    sentence_map = [{"startIdx": s["startIdx"], "endIdx": s["endIdx"]} for s in matched]
    (output_dir / "sentence_map.json").write_text(
        json.dumps(sentence_map, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    
    # auto_selected.json: silence gap indices (same as gen_analysis.js)
    gap_indices = [i for i, w in enumerate(words) if w.get("isGap") and (w.get("end", 0) - w.get("start", 0)) >= 0.2]
    (output_dir / "auto_selected.json").write_text(
        json.dumps(gap_indices, indent=2), encoding="utf-8"
    )
    
    # alignment_report.json: detailed alignment info
    report = {
        "total_manuscript_sentences": len(aligned_sentences),
        "matched": len(matched),
        "unmatched": len(unmatched),
        "avg_confidence": round(sum(s["confidence"] for s in matched) / len(matched), 3) if matched else 0,
        "unmatched_sentences": [
            {"text": s["text"][:80], "section": s["section"]}
            for s in unmatched
        ],
        "low_confidence_sentences": [
            {
                "idx": s["idx"],
                "text": s["text"][:80],
                "section": s["section"],
                "confidence": s["confidence"],
                "start_time": s.get("start_time", 0),
            }
            for s in matched if s["confidence"] < 0.5
        ],
    }
    (output_dir / "alignment_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    
    return report


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    video_dir = Path(sys.argv[1])
    words_file = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    manuscript_choice = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    
    # 1. Find manuscript
    manuscripts = find_manuscripts(video_dir)
    if not manuscripts:
        print("⚠ 未找到文稿文件，回退到静音分句（gen_analysis.js）")
        sys.exit(1)
    
    manuscript = ask_user_manuscript(manuscripts, manuscript_choice)
    print(f"📖 使用文稿: {manuscript.name}")
    
    # 2. Parse manuscript
    sentences = parse_manuscript(manuscript)
    print(f"📝 文稿句子: {len(sentences)}")
    
    # 3. Read Whisper transcript
    words_raw = words_file.read_bytes()
    for enc in ["utf-8", "gbk", "cp936"]:
        try:
            words = json.loads(words_raw.decode(enc))
            break
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    
    whisper_chars, char_map = flatten_whisper(words)
    print(f"🎤 Whisper 词数: {sum(1 for w in words if not w.get('isGap'))}")
    print(f"🔤 Whisper 字符数: {len(whisper_chars)}")
    
    # 4. Align
    print(f"\n🔗 对齐中...")
    aligned = align_manuscript_to_whisper(sentences, whisper_chars, char_map)
    
    matched = [s for s in aligned if s.get("matched")]
    unmatched = [s for s in aligned if not s.get("matched")]
    print(f"  ✅ 匹配: {len(matched)}/{len(aligned)}")
    print(f"  ❌ 未匹配: {len(unmatched)}")
    
    avg_conf = sum(s["confidence"] for s in matched) / len(matched) if matched else 0
    print(f"  📊 平均置信度: {avg_conf:.1%}")
    
    # 5. Generate outputs
    report = generate_outputs(aligned, words, output_dir)
    print(f"\n📁 输出目录: {output_dir}")
    print(f"  analysis.txt ({len(matched)} 句)")
    print(f"  sentence_map.json ({len(matched)} 段)")
    print(f"  auto_selected.json ({len(report.get('low_confidence_sentences', []))} 低置信)")
    
    # Show unmatched
    if unmatched:
        print(f"\n⚠ 未匹配的文稿句子:")
        for s in unmatched[:10]:
            print(f"  [{s['section']}] {s['text'][:60]}...")
    
    # Show low confidence
    low_conf = [s for s in matched if s["confidence"] < 0.5]
    if low_conf:
        print(f"\n⚠ 低置信度句子 ({len(low_conf)}):")
        for s in low_conf[:10]:
            print(f"  conf={s['confidence']:.0%} [{s['section']}] {s['text'][:60]}")


if __name__ == "__main__":
    main()
