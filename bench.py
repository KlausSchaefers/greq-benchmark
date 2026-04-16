import subprocess
import re
import json
import time
from dataclasses import dataclass


@dataclass
class BenchResult:
    results: list[dict]
    time: float




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

def run_greq(query: str, filepattern: str, n: int, w: float) -> BenchResult:
    """
    Run grep command with the given query and file pattern.
    
    Args:
        query (str): The search query/pattern for grep
        filepattern (str): The file pattern to search in (supports glob patterns)
    
    Returns:
        BenchResult: The result of the grep command with timing information
    """
    try:
        # Use shell=True to allow glob expansion, just like command line
        command = f'./bin/greq -f json -n {n} -w {w} "{query}" {filepattern}'
        start = time.perf_counter()
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True, 
            text=True, 
            check=False
        )
        #print(f"Command executed: {command}", result.stdout)
        elapsed = time.perf_counter() - start
        return BenchResult(results=json.loads(result.stdout), time=elapsed)
    except Exception as e:
        print(f"Error running grep command: {e}")
        return BenchResult(results=[], time=0.0)
    

def run_grep(query: str, filepattern: str, n: int) -> BenchResult:
    """
    Run grep command with the given query and file pattern.
    
    Args:
        query (str): The search query/pattern for grep
        filepattern (str): The file pattern to search in (supports glob patterns)
        n (int): Number of lines to return
    
    Returns:
        BenchResult: The result of the grep command with timing information
    """
    try:
        # Build an OR-regex from space-separated query terms and
        # pass it to grep. Use shell=True to allow glob expansion.
        # Split by literal space as requested.
        parts = [p for p in query.split(" ") if p != ""]
        if not parts:
            return BenchResult(results=[], time=0.0)

        # Escape regex-special characters in each part
        escaped = [re.escape(p) for p in parts]
        pattern = "|".join(escaped)

        # Protect double quotes in the pattern for shell interpolation
        pattern_for_shell = pattern.replace('"', '\\"')
        command = f'grep -Ei -n --color --max-count={n} "{pattern_for_shell}" {filepattern}'
        start = time.perf_counter()
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True, 
            text=True, 
            check=False
        )
        elapsed = time.perf_counter() - start

        return BenchResult(results=parse_grep_output(result.stdout), time=elapsed)
    except Exception as e:
        print(f"Error running grep command: {e}")
        return BenchResult(results=[], time=0.0)

def tets_sport():
    res = run_grep("Karate Okinawan", "./data/sport/*", 3)
    print(f'Result of grep command ({res.time:.4f}s):', json.dumps(res.results, indent=2))

def main():
    print("Hello from greq-benchmark!")
    # res = run_grep("Karate Okinawan", "./data/sport/*", 3)
    # print(f'Result of grep command ({res.time:.4f}s):')

    # res = run_greq("Karate", "./data/sport/*", 4, 0)
    # print(f'Result of greq command ({res.time:.4f}s):', len(res.results))
   
    res = run_greq("Karate", "./data/sport/*", 3, 0.4)
    print(f'Result of greq command ({res.time:.4f}s):', len(res.results))

if __name__ == "__main__":
    main()
