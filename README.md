# ToTheRoot — Autonomous AI Pentesting Framework

An autonomous penetration testing framework that uses local LLMs 
via MCP (Model Context Protocol) to orchestrate offensive security 
tools end-to-end — without per-step human input.

## What it does
- Plans and executes recon, exploitation, and post-exploitation
- Chains Nmap, Gobuster, SQLmap, and custom scripts automatically
- Uses Ollama for offline local LLM inference
- CPTS-grade methodology embedded as inline LLM context

## How it works
1. Provide a target
2. LLM plans the attack chain
3. Tools execute autonomously
4. Results fed back to LLM for next decision
5. Repeat until rooted

## Stack
Python · Ollama · MCP · Local LLM

## Status
Active development — college project under Prof. Manisha,
Dronacharya College of Engineering

## Disclaimer
For authorized penetration testing and educational purposes only.
Never use against systems you don't have explicit permission to test.

## Author
Parveen Rawat (Sh2d0w)
github.com/Parveen-Rawat
