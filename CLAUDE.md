# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese novel text processing project called "getDialog" that extracts character information and dialogue content from Chinese novel text files. The project is in early development stage with no implementation code yet.

## Project Structure

```
getDialog/
├── README.md           # Project documentation in Chinese
├── data/              # Input directory for novel text files
│   └── ziyang.txt     # Sample Chinese novel text file
├── doc/               # Documentation directory (empty)
└── src/               # Source code directory (empty, to be implemented)
```

## Development Status

This is a greenfield project with only planning documentation. The actual implementation needs to be built from scratch according to the requirements in README.md.

## Planned Features (from README.md)

- Text preprocessing and encoding conversion
- Chapter structure recognition
- Character name extraction  
- Dialogue content separation
- Structured data format output

## Input Data Format

- Text files in `data/` directory containing Chinese novels
- Current sample file: `ziyang.txt` (Chinese novel with chapter structure and dialogue)
- Text appears to use traditional/simplified Chinese characters with chapter markers like "第一章" (Chapter 1)

## Development Notes

- No build system, dependencies, or test framework configured yet
- No package.json, requirements.txt, or other configuration files present
- Implementation language not specified in documentation
- Text encoding appears to be an issue with the sample file (contains encoding artifacts)

## Recommended Next Steps for Implementation

1. Choose implementation language (Python recommended for Chinese text processing)
2. Set up project dependencies and build system
3. Implement text encoding detection and conversion
4. Create chapter segmentation logic
5. Develop character name recognition (likely requires Chinese NLP libraries)
6. Build dialogue extraction and formatting system