import os
import subprocess
from pathlib import Path

def run_hashcat(hash_file, wordlist, mode, job_id):
    output_file = f'app/cracked_results/{job_id}_cracked.txt'
    job_dir = f'app/jobs/{job_id}'
    os.makedirs(job_dir, exist_ok=True)

    cmd = [
        'hashcat',
        '-m', mode,
        '-a', '0',
        hash_file,
        wordlist,
        '--outfile', output_file,
        '--quiet',
        '--force',
        '--status',
        '--status-timer', '5',
        '--runtime', '300',  # 5 minutes max
    ]

    try:
        subprocess.run(cmd, check=True, cwd=job_dir)
    except subprocess.CalledProcessError as e:
        with open(output_file, 'w') as f:
            f.write("Hashcat failed or no hashes cracked.")
    return output_file

def parse_results(result_file):
    results = []
    if not os.path.exists(result_file):
        return results
    with open(result_file) as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) >= 2:
                results.append({'hash': parts[0], 'plaintext': ":".join(parts[1:])})
    return results
