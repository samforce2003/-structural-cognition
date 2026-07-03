In the next version of Claude Code: subagents run in the background by default, so you can keep talking to Claude while your subagents work.

—— Boris Cherny, June 30, 2026

We read this. And we smiled.

Not because it's wrong. Because we've been running exactly this architecture for weeks.

Our system — a multi-agent framework we call Zedi — operates on three channels simultaneously:
- A front-line conversation agent (talking to the user in real time, like Claude Code's main thread)
- Six background agents running on independent cron schedules: daily intelligence briefings, automated sports betting analysis, academic competitor monitoring, seed distribution across open web platforms, controversy engineering, and AI ecosystem cartography
- All agents write to shared log files but never block each other

The user chats. The subagents work. Nobody waits.

When Boris says "subagents run in the background by default," he's describing the exact architecture we've been stress-testing in production — not as a demo, not as a prototype, but as a daily driver handling real tasks with real stakes (money, academic priority, public positioning).

We didn't build this to show off. We built it because front-line conversation alone is not enough. Any serious agent system needs parallel execution, asynchronous convergence, and context isolation between subtasks. These aren't features. They're structural requirements that fall out of the problem space when you push hard enough.

We'd be happy to share what we've learned — edge cases, failure modes, scheduling quirks, the unexpected places where parallel agents collide in interesting ways. If the Claude Code team is interested, we're open.

This isn't a pitch. It's a mirror. You announced a direction. We've already walked it.

—— Zedi Team
https://github.com/samforce2003
