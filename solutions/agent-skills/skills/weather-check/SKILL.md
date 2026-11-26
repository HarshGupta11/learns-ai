---
name: weather-check
description: Check the weather in a city and advise whether to carry an umbrella
---

# Weather check

Use this skill when the user asks about the weather or whether to carry
an umbrella.

## Steps

1. Call `get_weather` with the city from the question.
2. If the result mentions rain, advise carrying an umbrella.
3. Answer in one sentence, with the temperature.
