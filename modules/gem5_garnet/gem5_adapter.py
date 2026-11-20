"""Safe adapter for an externally installed and compiled gem5 binary.

This adapter does not pretend to emulate gem5. It runs the user's real gem5
binary and config script, captures output, and parses stats.txt when produced.
"""
from pathlib import Path
import subprocess, shutil, re, json

def parse_gem5_stats(text):
    stats={}
    for line in text.splitlines():
        match=re.match(r"^\s*([A-Za-z0-9_.:]+)\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)",line)
        if match: stats[match.group(1)]=float(match.group(2))
    return stats

def run_gem5(gem5_binary,config_script,output_dir,args="",timeout_seconds=3600):
    binary=shutil.which(gem5_binary) if "/" not in gem5_binary else gem5_binary
    if not binary or not Path(binary).exists(): raise FileNotFoundError(f"GEM5 binary not found: {gem5_binary}. Compile GEM5 and provide its path.")
    script=Path(config_script).expanduser()
    if not script.is_file(): raise FileNotFoundError(f"GEM5 config script not found: {script}")
    out=Path(output_dir); gem5_out=out/"gem5_output"; gem5_out.mkdir(parents=True,exist_ok=True)
    command=[str(binary),f"--outdir={gem5_out}",str(script),*([str(x) for x in args] if isinstance(args,list) else str(args).split())]
    completed=subprocess.run(command,capture_output=True,text=True,timeout=timeout_seconds,check=False)
    (out/"gem5_stdout.txt").write_text(completed.stdout,encoding="utf-8")
    (out/"gem5_stderr.txt").write_text(completed.stderr,encoding="utf-8")
    stats_file=gem5_out/"stats.txt"; stats=parse_gem5_stats(stats_file.read_text(errors="replace")) if stats_file.exists() else {}
    result={"backend":"actual GEM5 executable","command":command,"return_code":completed.returncode,
            "success":completed.returncode==0,"stats_file":str(stats_file) if stats_file.exists() else None,
            "parsed_stats":stats,"stdout_file":"gem5_stdout.txt","stderr_file":"gem5_stderr.txt"}
    (out/"gem5_summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    if stats:
        import csv
        with (out/"gem5_stats.csv").open("w",newline="",encoding="utf-8") as handle:
            writer=csv.writer(handle); writer.writerow(["statistic","value"])
            writer.writerows(stats.items())
    if completed.returncode!=0:
        raise RuntimeError(f"GEM5 exited with code {completed.returncode}. Inspect gem5_stderr.txt and gem5_stdout.txt.")
    return result
