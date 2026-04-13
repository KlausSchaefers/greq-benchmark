import subprocess
import re
import json


def parse_grep_output(grep_output: str) -> list[dict]:
    """
    Parse grep output into structured format.
    
    Args:
        grep_output (str): Raw output from grep command
        query (str): The search query that was used
    
    Returns:
        list[dict]: List of dictionaries with file_path, content, matched_text, start_pos, end_pos
    """
    results = []
    if not grep_output:
        return results
    
    lines = grep_output.strip().split('\n')
    
    # Cache file contents to calculate absolute positions
    file_content_cache = {}
    
    for line in lines:
        if not line:
            continue
            
        # Parse grep output format: file_path:line_number:content
        parts = line.split(':', 2)
        if len(parts) < 3:
            continue
            
        file_path = parts[0]
        line_number = int(parts[1])
        content = parts[2]
       
        result = {
            "file_path": file_path,
            "line_number": line_number,
            "content": content
        }
        results.append(result)

    return results

def run_greq(query: str, filepattern: str) -> list[dict]:
    """
    Run grep command with the given query and file pattern.
    
    Args:
        query (str): The search query/pattern for grep
        filepattern (str): The file pattern to search in (supports glob patterns)
    
    Returns:
        list[dict]: The result of the grep command in structured format
    """
    try:
        # Use shell=True to allow glob expansion, just like command line
        command = f'./bin/greq -f json "{query}" {filepattern}'
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True, 
            text=True, 
            check=False
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running grep command: {e}")
        return []
    

def run_grep(query: str, filepattern: str) -> list[dict]:
    """
    Run grep command with the given query and file pattern.
    
    Args:
        query (str): The search query/pattern for grep
        filepattern (str): The file pattern to search in (supports glob patterns)
    
    Returns:
        list[dict]: The result of the grep command in structured format
    """
    try:
        # Build an OR-regex from space-separated query terms and
        # pass it to grep. Use shell=True to allow glob expansion.
        # Split by literal space as requested.
        parts = [p for p in query.split(" ") if p != ""]
        if not parts:
            return []

        # Escape regex-special characters in each part
        escaped = [re.escape(p) for p in parts]
        pattern = "|".join(escaped)

        # Protect double quotes in the pattern for shell interpolation
        pattern_for_shell = pattern.replace('"', '\\"')
        print(f"Running grep with pattern: {pattern_for_shell} on files: {filepattern}")

        command = f'grep -Ei -n --color "{pattern_for_shell}" {filepattern}'
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True, 
            text=True, 
            check=False
        )        
        return parse_grep_output(result.stdout)
    except Exception as e:
        print(f"Error running grep command: {e}")
        return []


def main():
    print("Hello from greq-benchmark!")
    res = run_grep("Karate Okinawan", "./data/sport/*")
    print('Result of grep command:', json.dumps(res, indent=2))

    # res = run_greq("Karate", "./data/sport/*.txt")
    # print('Result of greq command:', json.dumps(res, indent=2))
   

if __name__ == "__main__":
    main()
