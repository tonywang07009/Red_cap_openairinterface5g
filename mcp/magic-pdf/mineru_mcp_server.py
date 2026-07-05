#!/usr/bin/env python3
"""
MinerU MCP Server for Codex - Red_cap_openairinterface5g
Provides intelligent PDF parsing with auto-classification
Uses MinerU 3.x API
Author: Caramel_Bird
Version: 2.0 - Phase 2A (New API)
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

# MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# MinerU (New API)
try:
    from mineru.cli.common import do_parse
except ImportError:
    print("Error: mineru not found. Install with: pip install 'git+https://github.com/opendatalab/MinerU.git'", file=sys.stderr)
    sys.exit(1)


app = Server("mineru-mcp-server")


def auto_detect_output_dir(pdf_path: Path) -> tuple[Path, str]:
    """
    Intelligently determine PDF output directory based on filename/path classification
    
    Classification logic (priority from top to bottom):
        1. RedCap project specs -> redcap_doc/mineru_markdown/specs/
        2. RedCap evaluation papers -> redcap_doc/mineru_markdown/evaluation_papers/
        3. 3GPP Specifications (TS 38.xxx, 37.xxx) -> agent_doc/specs_cache/3gpp/
        4. O-RAN Specifications (E2SM, xApp, rApp) -> agent_doc/specs_cache/oran/
        5. Research Papers (IEEE, paper keywords) -> agent_doc/papers_cache/
        6. Experiment-related (taguchi, DoE) -> agent_doc/exp_cache/
        7. SDK Development Docs (xapp, rapp, dapp) -> agent_doc/specs_cache/oran/
        8. Others -> agent_doc/pdf_cache/
    
    Args:
        pdf_path: Path object of the PDF file
        
    Returns:
        Tuple of (output directory Path object, classification label)
    """
    
    filename = pdf_path.name.lower()
    parent_dir = pdf_path.parent.name.lower()
    path_text = str(pdf_path).lower()
    
    # Classification rule table (extensible)
    classification_rules = [
        # RedCap project-local document caches
        (lambda: 'redcap_doc/specs/' in path_text,
         'redcap_doc/mineru_markdown/specs', 'RedCap Project Spec'),
        (lambda: 'redcap_doc/evaluation_papers/' in path_text,
         'redcap_doc/mineru_markdown/evaluation_papers', 'RedCap Evaluation Paper'),

        # 3GPP Specifications
        (lambda: filename.startswith('ts ') or filename.startswith('ts_'), 
         'agent_doc/specs_cache/3gpp', '3GPP Spec'),
        (lambda: '38.' in filename or '37.' in filename or '36.' in filename,
         'agent_doc/specs_cache/3gpp', '3GPP Spec'),
        (lambda: 'ts_38_' in filename or 'ts_37_' in filename or 'ts_36_' in filename,
         'agent_doc/specs_cache/3gpp', '3GPP Spec'),
        
        # O-RAN Specifications
        (lambda: 'oran' in filename or 'e2sm' in filename or 'o-ran' in filename, 
         'agent_doc/specs_cache/oran', 'O-RAN Spec'),
        (lambda: 'xapp' in filename or 'rapp' in filename or 'dapp' in filename, 
         'agent_doc/specs_cache/oran', 'O-RAN SDK'),
        (lambda: 'ric' in filename, 
         'agent_doc/specs_cache/oran', 'O-RAN RIC'),
        
        # Generic Specifications
        (lambda: 'spec' in parent_dir or 'specification' in parent_dir, 
         'agent_doc/specs_cache/other', 'Generic Spec'),
        
        # Research Papers
        (lambda: 'paper' in parent_dir or 'ieee' in filename or 'acm' in filename, 
         'agent_doc/papers_cache', 'Research Paper'),
        (lambda: 'journal' in filename or 'conference' in filename, 
         'agent_doc/papers_cache', 'Research Paper'),
        
        # Experiment Design
        (lambda: 'taguchi' in filename or 'doe' in filename or 'experiment' in filename, 
         'agent_doc/exp_cache', 'Experiment Design'),
    ]
    
    # Check rules in order
    for condition, output_path, label in classification_rules:
        try:
            if condition():
                return Path(output_path), label
        except Exception:
            continue
    
    # Default classification
    return Path('agent_doc/pdf_cache'), 'Uncategorized'


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MinerU tools"""
    return [
        Tool(
            name="parse_pdf",
            description=(
                "Parse PDF document and convert to Markdown format.\n"
                "Auto-classification features:\n"
                "- 3GPP Specs -> specs_cache/3gpp/\n"
                "- O-RAN Specs -> specs_cache/oran/\n"
                "- Papers -> papers_cache/\n"
                "- Experiments -> exp_cache/\n"
                "- Others -> pdf_cache/"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Absolute path or relative path to PDF file from repo root"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": (
                            "Output directory (optional).\n"
                            "If not specified, system auto-classifies by filename.\n"
                            "If specified, uses the given directory."
                        )
                    },
                    "language": {
                        "type": "string",
                        "description": (
                            "MinerU language code. Defaults to 'ch' because the local "
                            "MCP environment currently has Chinese OCR weights installed."
                        )
                    },
                    "table_enable": {
                        "type": "boolean",
                        "description": "Enable table OCR. Defaults to false for stable RedCap cache generation."
                    },
                    "formula_enable": {
                        "type": "boolean",
                        "description": "Enable formula parsing. Defaults to false for stable RedCap cache generation."
                    }
                },
                "required": ["pdf_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute PDF parsing tool"""
    
    if name == "parse_pdf":
        pdf_path = Path(arguments["pdf_path"])
        
        # Intelligent output directory detection
        if "output_dir" in arguments and arguments["output_dir"]:
            output_dir = Path(arguments["output_dir"])
            classification = "User-specified"
        else:
            output_dir, classification = auto_detect_output_dir(pdf_path)

        language = arguments.get("language", "ch")
        table_enable = arguments.get("table_enable", False)
        formula_enable = arguments.get("formula_enable", False)
        
        # Check file existence
        if not pdf_path.exists():
            return [TextContent(
                type="text",
                text=f"ERROR: PDF file not found\nPath: {pdf_path}\n\nPlease verify the file path is correct."
            )]
        
        # Create output directory
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"ERROR: Cannot create output directory\nDirectory: {output_dir}\nReason: {str(e)}"
            )]
        
        try:
            # Read PDF bytes
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Call MinerU parser (new API)
            do_parse(
                output_dir=str(output_dir),
                pdf_file_names=[pdf_path.name],
                pdf_bytes_list=[pdf_bytes],
                p_lang_list=[language],
                backend='pipeline',     # Use pipeline backend
                parse_method='auto',    # Auto-detect parse method
                formula_enable=formula_enable,
                table_enable=table_enable,
                f_dump_md=True,         # Generate Markdown
                f_dump_middle_json=False,  # Skip intermediate JSON
                f_dump_model_output=False, # Skip model output
                f_dump_orig_pdf=False,     # Skip original PDF copy
            )
            
            # Find output Markdown file
            output_file = output_dir / f"{pdf_path.stem}.md"
            
            # MinerU may put output in subdirectory
            if not output_file.exists():
                # Search for .md files in output_dir
                md_files = list(output_dir.rglob("*.md"))
                if md_files:
                    output_file = md_files[0]
            
            if output_file.exists():
                content = output_file.read_text(encoding='utf-8')
                content_preview = content[:800] if len(content) > 800 else content
                
                return [TextContent(
                    type="text",
                    text=(
                        f"SUCCESS: PDF parsing completed!\n\n"
                        f"Source File: {pdf_path.name}\n"
                        f"Classification: {classification}\n"
                        f"Output Path: {output_file}\n"
                        f"File Size: {len(content)} characters\n\n"
                        f"{'='*60}\n"
                        f"Content Preview (first 800 chars):\n"
                        f"{'='*60}\n\n"
                        f"{content_preview}\n\n"
                        f"{'='*60}\n"
                        f"TIP: Full content saved at {output_file}"
                    )
                )]
            else:
                return [TextContent(
                    type="text",
                    text=(
                        f"WARNING: Parsing completed but output file not found\n\n"
                        f"Expected output: {output_file}\n"
                        f"Output directory contents:\n"
                        f"{list(output_dir.rglob('*'))}\n\n"
                        f"Please check MinerU output."
                    )
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=(
                    f"ERROR: PDF parsing failed\n\n"
                    f"File: {pdf_path}\n"
                    f"Error Message: {str(e)}\n\n"
                    f"Common Solutions:\n"
                    f"1. Verify PDF file is not corrupted\n"
                    f"2. Check mineru is correctly installed\n"
                    f"3. Ensure sufficient disk space"
                )
            )]
    
    return [TextContent(
        type="text", 
        text=f"ERROR: Unknown tool: {name}\nAvailable tools: parse_pdf"
    )]


async def main():
    """Start MCP Server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream, 
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
