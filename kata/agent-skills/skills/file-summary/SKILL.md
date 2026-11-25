---
name: file-summary
description: Read a file and summarize its contents in one line
---

# File summary

Use this skill when the user asks what is in a file.

## Steps

1. Call `read_file` with the path from the question.
2. Summarize the contents in one sentence.
3. If the file is unknown, say so instead of guessing.
