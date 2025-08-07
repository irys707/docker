import subprocess, tempfile, json, os

def run_hashcat(hashes, hash_type, wordlist_path, job_id):
    tmp_hash_file = os.path.join(tempfile.gettempdir(), f"{job_id}_hashes.txt")
    with open(tmp_hash_file, "w") as f:
        f.write(hashes)

    result_file = f"app/storage/results/{job_id}_results.json"
    cmd = [
        "hashcat",
        "-m", hash_type,
        tmp_hash_file,
        wordlist_path,
        "--quiet",
        "--outfile", f"{tmp_hash_file}.out",
        "--force"
    ]

    subprocess.run(cmd, timeout=300)

    cracked = []
    if os.path.exists(f"{tmp_hash_file}.out"):
        with open(f"{tmp_hash_file}.out") as f:
            for line in f:
                cracked.append({"cracked": line.strip()})

    with open(result_file, "w") as f:
        json.dump(cracked, f)
    return result_file
