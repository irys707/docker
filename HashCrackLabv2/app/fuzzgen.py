import itertools, string, os

def generate_fuzz_wordlist():
    fuzz_path = "app/storage/uploads/auto_fuzz.txt"
    with open(fuzz_path, "w") as f:
        for pwd in ["admin", "123456", "qwerty"]:
            f.write(f"{pwd}\n")
        for p in itertools.product(string.ascii_lowercase, repeat=5):
            f.write("".join(p) + "\n")
        for p in itertools.product(string.digits, repeat=4):
            f.write("".join(p) + "\n")
    return fuzz_path
