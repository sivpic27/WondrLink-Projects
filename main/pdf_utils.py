# pdf_utils.py
import os
import re
import logging
from typing import List, Tuple
import math

logger = logging.getLogger("pdf_utils")
logging.basicConfig(level=logging.INFO)

def _write_debug(path: str, suffix: str, content: str):
    try:
        out = f"{path}.{suffix}"
        with open(out, "w", encoding="utf-8") as f:
            f.write(content or "")
        logger.info("Wrote debug file: %s (len=%s)", out, len(content or ""))
    except Exception:
        logger.exception("Failed to write debug file")

# pdfplumber extraction
def extract_text_pdfplumber(path: str) -> str:
    try:
        import pdfplumber
    except ImportError as e:
        logger.warning("pdfplumber not installed: %s", e)
        return ""
    try:
        parts = []
        with pdfplumber.open(path) as pdf:
            logger.info("pdfplumber opened PDF with %d pages: %s", len(pdf.pages), path)
            for i, page in enumerate(pdf.pages):
                t = page.extract_text()
                if t:
                    parts.append(t)
        text = "\n\n".join(parts)
        logger.info("pdfplumber extracted %d chars from %s", len(text), path)
        return text
    except Exception as e:
        logger.exception("pdfplumber extraction failed for %s: %s", path, e)
        return ""

# PyPDF2 extraction fallback
def extract_text_pypdf2(path: str) -> str:
    try:
        from PyPDF2 import PdfReader
    except Exception:
        logger.info("PyPDF2 not installed")
        return ""
    try:
        reader = PdfReader(path)
        parts = []
        for p in reader.pages:
            try:
                t = p.extract_text() or ""
            except Exception:
                t = ""
            if t:
                parts.append(t)
        text = "\n\n".join(parts)
        _write_debug(path, "extract_text.pypdf2", text)
        return text
    except Exception:
        logger.exception("PyPDF2 extraction failed")
        return ""

# OCR fallback (optional; needs pdf2image, pytesseract, poppler, tesseract)
def extract_text_ocr(path: str) -> str:
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception:
        logger.info("pdf2image/pytesseract not available")
        return ""
    try:
        images = convert_from_path(path, dpi=200)
        parts = []
        for i, img in enumerate(images):
            txt = pytesseract.image_to_string(img)
            parts.append(txt)
        text = "\n\n".join(parts)
        _write_debug(path, "extract_text.ocr", text)
        return text
    except Exception:
        logger.exception("OCR extraction failed")
        return ""

# Public helper: extract_text(path) -> raw text (tries methods in order)
def extract_text(path: str) -> str:
    if not os.path.exists(path):
        logger.error("extract_text: file not found: %s", path)
        return ""
    # 1) pdfplumber
    t = extract_text_pdfplumber(path)
    if t and len(t.strip()) > 50:
        return t
    # 2) pypdf2
    t2 = extract_text_pypdf2(path)
    if t2 and len(t2.strip()) > 50:
        return t2
    # 3) ocr
    t3 = extract_text_ocr(path)
    if t3 and len(t3.strip()) > 20:
        return t3
    # nothing found
    _write_debug(path, "extract_text.empty", "")
    logger.warning("extract_text: no text found for %s", path)
    return ""

# Enhanced chunking with medical awareness and overlap
def chunk_text(text: str, max_chars: int = 1500, overlap_percent: float = 0.2) -> List[Tuple[str, dict]]:
    """
    Enhanced chunking with sliding window overlap to preserve context across boundaries.

    Args:
        text: The text to chunk
        max_chars: Maximum characters per chunk
        overlap_percent: Percentage of overlap between chunks (0.2 = 20%)

    Returns:
        List of tuples: (chunk_text, metadata_dict)
    """
    if not text:
        return []

    # Calculate overlap size
    overlap_size = int(max_chars * overlap_percent)
    slide_size = max_chars - overlap_size  # How far to slide the window

    # Medical document section patterns (NCCN, research papers, etc.)
    section_patterns = [
        r'^[A-Z][A-Z\s]+\n',  # ALL CAPS headers
        r'^\d+\.\s+[A-Z][a-z]',  # Numbered sections (1. Introduction)
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:\s*\n',  # Title Case headers with colon
        r'^(?:Background|Introduction|Methods|Results|Discussion|Conclusion|Treatment|Diagnosis|Management|Recommendations?|Guidelines?)[:.]',
        r'^(?:BACKGROUND|INTRODUCTION|METHODS|RESULTS|DISCUSSION|CONCLUSION|TREATMENT|DIAGNOSIS|MANAGEMENT|RECOMMENDATIONS?|GUIDELINES?)[:.]',
        r'^\s*[A-Z]{2,}(?:\s+[A-Z]{2,})*\s*$',  # Stand-alone ALL CAPS lines
    ]

    # Split text into lines for processing
    lines = text.split('\n')
    all_lines_with_headers = []
    current_section = "Unknown Section"

    # First pass: identify sections and tag lines
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Check if this line is a section header
        is_section_header = any(re.match(pattern, line_stripped, re.IGNORECASE) for pattern in section_patterns)
        if is_section_header:
            current_section = line_stripped[:100]  # Store first 100 chars as section name

        all_lines_with_headers.append((line_stripped, current_section))

    # Second pass: create overlapping chunks
    chunks_with_metadata = []
    start_idx = 0
    chunk_position = 0

    while start_idx < len(all_lines_with_headers):
        current_chunk_lines = []
        current_length = 0
        current_section = all_lines_with_headers[start_idx][1] if start_idx < len(all_lines_with_headers) else "Unknown"
        end_idx = start_idx

        # Build chunk up to max_chars
        for idx in range(start_idx, len(all_lines_with_headers)):
            line_text, section = all_lines_with_headers[idx]
            line_length = len(line_text) + 1

            if current_length + line_length > max_chars and current_chunk_lines:
                break

            current_chunk_lines.append(line_text)
            current_length += line_length
            end_idx = idx

        # Create chunk with metadata
        if current_chunk_lines:
            chunk_text = '\n'.join(current_chunk_lines)

            # Only add if chunk is substantial (>= 50 chars)
            if len(chunk_text.strip()) >= 50:
                metadata = {
                    'position': chunk_position,
                    'section': current_section,
                    'char_start': start_idx,
                    'char_end': end_idx,
                    'has_overlap': chunk_position > 0  # First chunk has no overlap
                }
                chunks_with_metadata.append((chunk_text, metadata))
                chunk_position += 1

        # Calculate next starting position with overlap
        # Find the line index that's approximately slide_size characters away
        chars_to_skip = 0
        lines_to_skip = 0
        for idx in range(start_idx, end_idx + 1):
            chars_to_skip += len(all_lines_with_headers[idx][0]) + 1
            lines_to_skip += 1
            if chars_to_skip >= slide_size:
                break

        start_idx += max(1, lines_to_skip)  # Ensure we always advance at least 1 line

        # Break if we can't make progress
        if start_idx >= len(all_lines_with_headers):
            break

    logger.info(f"Created {len(chunks_with_metadata)} overlapping chunks (overlap: {overlap_percent*100}%) from text of length {len(text)}")
    return chunks_with_metadata

# Enhanced semantic search with medical term awareness
def create_term_vector(text: str) -> dict:
    """Create a term frequency vector with medical term boosting"""
    
    # Medical terms that should be weighted higher in search
    medical_terms = {
        'cancer', 'tumor', 'oncology', 'chemotherapy', 'radiation', 'surgery', 'treatment', 
        'therapy', 'diagnosis', 'prognosis', 'metastasis', 'stage', 'grade', 'biopsy',
        'lymph', 'node', 'malignant', 'benign', 'carcinoma', 'sarcoma', 'leukemia', 
        'lymphoma', 'myeloma', 'breast', 'lung', 'colon', 'prostate', 'ovarian',
        'nccn', 'guideline', 'protocol', 'clinical', 'trial', 'study', 'patient',
        'survival', 'response', 'progression', 'relapse', 'remission', 'palliative',
        'adjuvant', 'neoadjuvant', 'systemic', 'local', 'regional', 'distant'
    }
    
    # Clean and tokenize text
    text_lower = text.lower()
    # Remove special characters but keep medical abbreviations
    text_clean = re.sub(r'[^\w\s\-\.]', ' ', text_lower)
    words = text_clean.split()
    
    # Create term frequency vector
    term_freq = {}
    total_words = len(words)
    
    for word in words:
        word = word.strip('.-')
        if len(word) > 2:  # Skip very short words
            term_freq[word] = term_freq.get(word, 0) + 1
    
    # Apply medical term boosting
    for term in term_freq:
        if term in medical_terms:
            term_freq[term] *= 2.0  # Boost medical terms
        elif any(med_term in term for med_term in medical_terms):
            term_freq[term] *= 1.5  # Partial boost for terms containing medical terms
    
    # Normalize by document length
    for term in term_freq:
        term_freq[term] = term_freq[term] / total_words
    
    return term_freq

def calculate_similarity(query_vector: dict, doc_vector: dict) -> float:
    """Calculate cosine similarity between query and document vectors"""
    
    # Get intersection of terms
    common_terms = set(query_vector.keys()) & set(doc_vector.keys())
    
    if not common_terms:
        return 0.0
    
    # Calculate dot product
    dot_product = sum(query_vector[term] * doc_vector[term] for term in common_terms)
    
    # Calculate magnitudes
    query_magnitude = math.sqrt(sum(freq ** 2 for freq in query_vector.values()))
    doc_magnitude = math.sqrt(sum(freq ** 2 for freq in doc_vector.values()))
    
    if query_magnitude == 0 or doc_magnitude == 0:
        return 0.0
    
    # Cosine similarity
    similarity = dot_product / (query_magnitude * doc_magnitude)
    
    # Add exact phrase matching bonus
    query_text = ' '.join(query_vector.keys())
    doc_text = ' '.join(doc_vector.keys())
    
    # Check for exact phrase matches (boost similarity)
    query_phrases = [' '.join(query_text.split()[i:i+2]) for i in range(len(query_text.split())-1)]
    phrase_bonus = 0
    for phrase in query_phrases:
        if len(phrase.strip()) > 4 and phrase in doc_text:
            phrase_bonus += 0.1
    
    return min(similarity + phrase_bonus, 1.0)

def search_chunks(query: str, chunks: List[str], top_k: int = 5) -> List[str]:
    """Enhanced semantic search with medical context awareness"""
    
    if not chunks:
        return []
    
    if not query.strip():
        return chunks[:top_k]
    
    logger.info(f"Searching {len(chunks)} chunks for query: '{query[:50]}...'")
    
    # Create query vector
    query_vector = create_term_vector(query)
    
    # Score all chunks
    scored_chunks = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        chunk_vector = create_term_vector(chunk)
        similarity = calculate_similarity(query_vector, chunk_vector)
        
        # Additional scoring factors
        
        # 1. Exact keyword matches (case-insensitive)
        query_words = set(query.lower().split())
        chunk_words = set(chunk.lower().split())
        exact_matches = len(query_words & chunk_words)
        exact_bonus = exact_matches * 0.1
        
        # 2. Medical relevance bonus
        medical_keywords = ['treatment', 'therapy', 'diagnosis', 'prognosis', 'cancer', 'tumor', 'stage', 'grade']
        medical_relevance = sum(1 for kw in medical_keywords if kw in chunk.lower()) * 0.05
        
        # 3. Length penalty for very short chunks
        length_penalty = 0 if len(chunk) > 200 else -0.1
        
        # 4. Position bonus (earlier chunks might be more important in guidelines)
        position_bonus = (len(chunks) - i) / len(chunks) * 0.02
        
        final_score = similarity + exact_bonus + medical_relevance + length_penalty + position_bonus
        
        scored_chunks.append((final_score, chunk, i))
    
    # Sort by score (descending)
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Return top_k results
    result_chunks = []
    for score, chunk, idx in scored_chunks[:top_k]:
        if score > 0.05:  # Only return chunks with meaningful similarity
            result_chunks.append(chunk)
        else:
            break
    
    # If no good matches found, return some chunks anyway (fallback)
    if not result_chunks and chunks:
        result_chunks = chunks[:min(3, len(chunks))]
        logger.info("No high-similarity chunks found, returning fallback chunks")
    
    logger.info(f"Returning {len(result_chunks)} chunks with scores: {[round(x[0], 3) for x in scored_chunks[:len(result_chunks)]]}")
    
    return result_chunks

# Public: process_pdf -> list of chunks
def process_pdf(path: str) -> List[str]:
    """
    Extract text from PDF and chunk it with overlap.
    Returns list of chunk strings (metadata is stored internally but not returned for backward compatibility)
    """
    logger.info("Processing PDF: %s", path)
    raw = extract_text(path)
    if not raw:
        logger.warning("No text extracted from PDF: %s", path)
        return []

    logger.info("Extracted %d chars, now chunking...", len(raw))
    # Get chunks with metadata
    chunks_with_metadata = chunk_text(raw)

    # Extract just the text for backward compatibility
    # (Future: we could use metadata for better search/ranking)
    chunk_texts = [ct for ct, metadata in chunks_with_metadata]

    logger.info("Created %d chunks from %s", len(chunk_texts), path)
    return chunk_texts