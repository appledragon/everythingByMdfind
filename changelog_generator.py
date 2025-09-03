#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Changelog Generator

根据git tag来生成一个change log, 要用git diff 来总结
Generate changelog based on git tags using git diff to summarize changes.

Usage:
    python3 changelog_generator.py [output_file]

If no output file is specified, prints to stdout.
"""

import subprocess
import sys
import re
from datetime import datetime
from typing import List, Tuple, Optional


def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return the output."""
    try:
        result = subprocess.run(['git'] + cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # For git repo check, we want to be silent
        if cmd == ['rev-parse', '--git-dir']:
            raise
        # For other commands, show warnings but continue
        print(f"Warning: Git command failed: {' '.join(['git'] + cmd)}", file=sys.stderr)
        return ""


def get_git_tags() -> List[Tuple[str, str]]:
    """Get all git tags with their commit dates, sorted by version."""
    # Get tags with their commit dates
    tag_output = run_git_command(['tag', '--sort=-version:refname', '--format=%(refname:short)|%(creatordate:short)'])
    
    if not tag_output:
        return []
    
    tags = []
    for line in tag_output.split('\n'):
        if '|' in line:
            tag, date = line.split('|', 1)
            tags.append((tag.strip(), date.strip()))
        else:
            # Fallback if date format is not available
            tag = line.strip()
            if tag:
                tags.append((tag, ""))
    
    # Sort by version (reverse order, newest first)
    return tags


def get_first_commit() -> str:
    """Get the hash of the first commit."""
    return run_git_command(['rev-list', '--max-parents=0', 'HEAD'])


def get_commit_date(commit: str) -> str:
    """Get the date of a commit."""
    return run_git_command(['show', '-s', '--format=%ci', commit])


def summarize_diff(from_ref: str, to_ref: str) -> dict:
    """Summarize the diff between two git references."""
    # Get basic diff stats
    diff_stats = run_git_command(['diff', '--numstat', f'{from_ref}..{to_ref}'])
    
    # Get list of changed files
    changed_files = run_git_command(['diff', '--name-only', f'{from_ref}..{to_ref}'])
    
    # Get commit messages between the refs
    commit_messages = run_git_command(['log', '--oneline', f'{from_ref}..{to_ref}'])
    
    # If no diff (e.g., single commit or same refs), try to get files in the commit
    if not diff_stats and not changed_files:
        # For a single commit, show what files it contains
        files_in_commit = run_git_command(['ls-tree', '--name-only', '-r', to_ref])
        if files_in_commit:
            changed_files = files_in_commit
            # Get the commit message for this specific commit
            if not commit_messages:
                commit_messages = run_git_command(['log', '--oneline', '-1', to_ref])
    
    # Parse diff stats
    total_additions = 0
    total_deletions = 0
    file_changes = []
    
    if diff_stats:
        for line in diff_stats.split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 3:
                    additions = parts[0] if parts[0] != '-' else '0'
                    deletions = parts[1] if parts[1] != '-' else '0'
                    filename = parts[2]
                    
                    try:
                        add_count = int(additions)
                        del_count = int(deletions)
                        total_additions += add_count
                        total_deletions += del_count
                        file_changes.append({
                            'file': filename,
                            'additions': add_count,
                            'deletions': del_count
                        })
                    except ValueError:
                        # Handle binary files or other edge cases
                        file_changes.append({
                            'file': filename,
                            'additions': 0,
                            'deletions': 0
                        })
    
    return {
        'total_additions': total_additions,
        'total_deletions': total_deletions,
        'files_changed': len([f for f in changed_files.split('\n') if f.strip()]) if changed_files else 0,
        'file_changes': file_changes,
        'changed_files': [f for f in changed_files.split('\n') if f.strip()] if changed_files else [],
        'commits': [c for c in commit_messages.split('\n') if c.strip()] if commit_messages else []
    }


def generate_changelog() -> str:
    """Generate the complete changelog."""
    tags = get_git_tags()
    
    changelog_lines = [
        "# Changelog",
        "",
        "All notable changes to this project will be documented in this file.",
        "",
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),",
        "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
        ""
    ]
    
    # Check for unreleased changes (changes since the last tag)
    if tags:
        latest_tag = tags[0][0]
        latest_tag_commit = run_git_command(['rev-list', '-n', '1', latest_tag])
        head_commit = run_git_command(['rev-parse', 'HEAD'])
        
        # Only show unreleased section if HEAD is different from the latest tag
        if latest_tag_commit != head_commit:
            unreleased_diff = summarize_diff(latest_tag, "HEAD")
            
            if unreleased_diff['files_changed'] > 0 or unreleased_diff['commits']:
                changelog_lines.append("## [Unreleased]")
                changelog_lines.append("")
                
                # Add summary statistics
                if unreleased_diff['files_changed'] > 0:
                    changelog_lines.append(f"**Changes Summary:**")
                    changelog_lines.append(f"- {unreleased_diff['files_changed']} files changed")
                    if unreleased_diff['total_additions'] > 0 or unreleased_diff['total_deletions'] > 0:
                        changelog_lines.append(f"- {unreleased_diff['total_additions']} lines added")
                        changelog_lines.append(f"- {unreleased_diff['total_deletions']} lines deleted")
                    changelog_lines.append("")
                
                # Add commit messages
                if unreleased_diff['commits']:
                    changelog_lines.append("**Commits:**")
                    for commit in unreleased_diff['commits']:
                        if commit.strip():
                            changelog_lines.append(f"- {commit}")
                    changelog_lines.append("")
                
                # Add changed files (limit to avoid overly long output)
                if unreleased_diff['changed_files'] and len(unreleased_diff['changed_files']) <= 20:
                    changelog_lines.append("**Modified Files:**")
                    for file in unreleased_diff['changed_files']:
                        if file.strip():
                            changelog_lines.append(f"- `{file}`")
                    changelog_lines.append("")
                elif len(unreleased_diff['changed_files']) > 20:
                    changelog_lines.append("**Modified Files:**")
                    changelog_lines.append(f"- {len(unreleased_diff['changed_files'])} files modified (too many to list)")
                    changelog_lines.append("")
                
                changelog_lines.append("---")
                changelog_lines.append("")
    
    if not tags:
        changelog_lines.append("No git tags found in this repository.")
        changelog_lines.append("")
        return '\n'.join(changelog_lines)
    
    # Process each tag
    for i, (current_tag, current_date) in enumerate(tags):
        # Determine the previous reference
        if i < len(tags) - 1:
            # Compare with previous tag
            previous_tag = tags[i + 1][0]
            from_ref = previous_tag
        else:
            # For the oldest tag, try to compare with first commit
            first_commit = get_first_commit()
            if first_commit and first_commit != run_git_command(['rev-list', '-n', '1', current_tag]):
                from_ref = first_commit
            else:
                # If we can't find a meaningful diff, show the tag contents
                from_ref = None
        
        to_ref = current_tag
        
        # Get diff summary
        if from_ref:
            diff_summary = summarize_diff(from_ref, to_ref)
        else:
            # Show what's in this tag/commit
            diff_summary = summarize_diff("", to_ref)
        
        # Add version header
        version_date = current_date if current_date else "Unknown Date"
        changelog_lines.append(f"## [{current_tag}] - {version_date}")
        changelog_lines.append("")
        
        # Add summary statistics
        if diff_summary['files_changed'] > 0:
            changelog_lines.append(f"**Changes Summary:**")
            changelog_lines.append(f"- {diff_summary['files_changed']} files changed")
            if diff_summary['total_additions'] > 0 or diff_summary['total_deletions'] > 0:
                changelog_lines.append(f"- {diff_summary['total_additions']} lines added")
                changelog_lines.append(f"- {diff_summary['total_deletions']} lines deleted")
            changelog_lines.append("")
        
        # Add commit messages
        if diff_summary['commits']:
            changelog_lines.append("**Commits:**")
            for commit in diff_summary['commits']:
                if commit.strip():
                    changelog_lines.append(f"- {commit}")
            changelog_lines.append("")
        
        # Add changed files (limit to avoid overly long output)
        if diff_summary['changed_files'] and len(diff_summary['changed_files']) <= 20:
            changelog_lines.append("**Modified Files:**")
            for file in diff_summary['changed_files']:
                if file.strip():
                    changelog_lines.append(f"- `{file}`")
            changelog_lines.append("")
        elif len(diff_summary['changed_files']) > 20:
            changelog_lines.append("**Modified Files:**")
            changelog_lines.append(f"- {len(diff_summary['changed_files'])} files modified (too many to list)")
            changelog_lines.append("")
        
        # Add detailed file changes if not too many
        if diff_summary['file_changes'] and len(diff_summary['file_changes']) <= 10:
            changelog_lines.append("**Detailed Changes:**")
            for change in diff_summary['file_changes']:
                if change['additions'] > 0 or change['deletions'] > 0:
                    changelog_lines.append(
                        f"- `{change['file']}`: +{change['additions']} -{change['deletions']}"
                    )
            changelog_lines.append("")
        
        changelog_lines.append("---")
        changelog_lines.append("")
    
    # Add footer
    changelog_lines.append("*This changelog was automatically generated using git tags and diff summaries.*")
    
    return '\n'.join(changelog_lines)


def main():
    """Main function."""
    # Check for help
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        print("\nOptions:")
        print("  -h, --help    Show this help message")
        print("\nExamples:")
        print("  python3 changelog_generator.py                    # Print to stdout")
        print("  python3 changelog_generator.py CHANGELOG.md       # Save to file")
        print("  python3 changelog_generator.py | head -20         # View first 20 lines")
        return
    
    # Check if we're in a git repository
    try:
        run_git_command(['rev-parse', '--git-dir'])
    except:
        print("Error: Not in a git repository.", file=sys.stderr)
        sys.exit(1)
    
    # Generate changelog
    changelog = generate_changelog()
    
    # Output to file or stdout
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        output_file = sys.argv[1]
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(changelog)
            print(f"Changelog written to {output_file}")
        except IOError as e:
            print(f"Error writing to file {output_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(changelog)


if __name__ == "__main__":
    main()