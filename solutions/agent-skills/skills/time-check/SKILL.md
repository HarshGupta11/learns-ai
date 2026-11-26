---
name: time-check
description: Get the current time of the system in particular timezone
---

# Time check

Use this skill when the user asks about the current time in any particular timezone

## Steps

1. Call `time_check` with the timezone from the question.
2. If the `time_check` errored out, then say so in the response.
3. Never fabricate the time response in case of error in tool `time_check`.
