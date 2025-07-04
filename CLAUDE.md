# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese novel text processing project called "getDialog" that extracts character information and dialogue content from Chinese novel text files. The project processes Chinese novels through a multi-step pipeline including encoding conversion, chapter structure recognition, and character extraction using AI models.

## Project Structure

```
getDialog/
├── README.md           # Project documentation in Chinese
├── requirements.txt    # Python dependencies (PyTorch, Transformers, etc.)
├── data/              # Input directory for novel text files
├── output/            # Output directory for processed results
├── models/            # Directory for downloaded AI models
├── bin/               # Binary/executable files
├── doc/               # Documentation directory
└── src/py/            # Python source code
    ├── main.py        # Main execution entry point
    ├── utils/         # Utility modules
    │   └── constants.py
    └── steps/         # Processing steps
        ├── step01_encoding/     # Text encoding conversion
        ├── step02_chapter/      # Chapter structure recognition
        ├── step03_character/    # Character extraction (Qwen model)
        ├── step04_dialogue/     # Dialogue extraction
        └── step05_formatting/   # Output formatting
```

## Development Commands

The project uses Python with a centralized main.py entry point:

```bash
# Environment setup and dependency installation
python src/py/main.py --step setup --action install

# Text encoding conversion
python src/py/main.py --step encoding --input data/ziyang.txt --output data/ziyang_utf8.txt

# Chapter structure recognition
python src/py/main.py --step chapter --input data/ziyang_utf8.txt --output output/

# Qwen model management
python src/py/main.py --step model --action download --source modelscope
python src/py/main.py --step model --action verify
python src/py/main.py --step model --action info

# Run complete pipeline
python src/py/main.py --step all --input data/ziyang.txt --output output/
```

## Architecture Overview

The project follows a multi-step processing pipeline:

1. **Step 1 - Encoding Conversion**: Detects and converts text encoding to UTF-8 using chardet
2. **Step 2 - Chapter Recognition**: Parses chapter/volume structure using regex patterns, generates visualizations
3. **Step 3 - Character Extraction**: Uses Qwen LLM for character name recognition
4. **Step 4 - Dialogue Extraction**: Separates dialogue content from narrative text
5. **Step 5 - Formatting**: Outputs structured data in various formats

## Key Dependencies

- PyTorch >= 2.0.0 for deep learning models
- Transformers >= 4.37.0 for Qwen model integration
- chardet for encoding detection
- Various utility libraries (tiktoken, einops, peft, etc.)

## Model Management

The project uses Qwen models for character extraction:
- Models are downloaded to `models/` directory
- Supports both ModelScope and Hugging Face sources
- Model verification and info commands available

## Input/Output Format

- **Input**: Chinese text files in `data/` directory
- **Output**: Structured data in `output/` directory including:
  - Chapter structure visualizations (text, tree, HTML, JSON)
  - Character information extraction
  - Dialogue content separation