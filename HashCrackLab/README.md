# 🔓 HashCrackLab

A secure, Dockerized Flask web app to automate hash cracking with Hashcat.

## 🚀 Features
- Upload or paste hashes (MD5, SHA1, NTLM, etc.)
- Select from bundled or custom wordlists
- Automated cracking with Hashcat
- Clean UI with job isolation and result downloads

## 🐳 Docker Usage

```bash
docker build -t hashcracklab .
docker run -p 5000:5000 \
  -v $(pwd)/app/wordlists:/app/app/wordlists \
  -v $(pwd)/app/cracked_results:/app/app/cracked_results \
  -e FLASK_SECRET=S3cr3t! \
  hashcracklab
