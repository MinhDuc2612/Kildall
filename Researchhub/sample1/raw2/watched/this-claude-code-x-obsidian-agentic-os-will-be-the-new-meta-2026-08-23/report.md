---
source: https://www.youtube.com/watch?v=njHuj8OxIVI
title: This Claude Code x Obsidian Agentic OS Will Be The New Meta
duration: 24:17
watched_at: 2026-08-23T21:52:12.474991+07:00
intent: research about it, identify the tool/project/technique being discussed, deep-research topic
hero_frames: [frame_0001.jpg, frame_0015.jpg, frame_0017.jpg, frame_0033.jpg, frame_0049.jpg]
transcript_source: captions
---

# This Claude Code x Obsidian Agentic OS Will Be The New Meta

## TL;DR

- The video (Chase AI / "Chase AI" channel) shows how to build a personal "Claude OS" — a Claude Code-powered agentic workflow wrapped in a custom Obsidian community plugin ("Command Center" / labeled "AGENTIC OS" on screen) that acts as a visual dashboard, not a new agent framework or product.
- Three real components stack together: (1) a UI layer — a bespoke Obsidian plugin Claude Code wrote and installed itself, showing metrics/schedule/skills/research reports; (2) a skills+automations backbone — day-to-day tasks codified as Claude Code skills, promoted to scheduled automations once proven; (3) an Obsidian "memory" layer that is really a navigation map (raw/wiki/output folders + index.md files), directly modeled on Andrej Karpathy's April viral tweet about Claude Code + Obsidian.
- A fully local voice-control layer is bolted on: mic audio → faster-whisper (open-source, local) STT → Claude Haiku 4.5 (swappable for a local model) routes the transcribed command into 3 tiers — Tier 1 = run a named skill, Tier 2 = answer from an existing report/metric (fast, no fresh research), Tier 3 = spin up a full headless `claude -p` run for open-ended tasks — then Kokoro (open-source) TTS speaks the reply back.
- The presenter is explicit that the dashboard/UI is cosmetic on top of substance: without the skills+automations backbone already built, the visual command center is "a zero-substance visual spectacle."
- This is squarely an "agentic OS" build video — it directly frames itself as building "your entire Claude OS" using Claude Code + Obsidian + a self-built plugin + local voice, which is exactly on-topic for an agentic-OS research doc.

## Key moments

- **[00:02] Hook / thesis** — "You are using Claude code in Obsidian the wrong way" — claims most people barely scratch Obsidian's surface as a command center for a full Claude OS (fleet of skills, automations, memory layer, visual wrapper). `frame_0001.jpg`
- **[00:41] Prior iterations shown** — a previous web-based Claude OS version (with local voice) and an older Obsidian version are shown before explaining the current merged setup.
- **[01:16] The dashboard itself** — "AGENTIC OS" command center plugin on screen: a single big metric front-and-center, token usage, social metrics, Google Calendar-pulled schedule/tasks, morning headlines, and clickable skill/automation buttons. `frame_0015.jpg`, `frame_0017.jpg`
- **[02:52-03:29] Live voice demo #1** — presenter says "what was the biggest AI news story for today?", the local voice pipeline answers about a Claude watermark rollout and "Deep Seek Harness" trending on GitHub — pulled from an already-run report, not live web search (hence fast).
- **[04:15-04:40] Live voice demo #2, tabbed out** — asks "what's the biggest thing on my schedule today?" while inside the Claude desktop app (not Obsidian); voice mode answers about a sponsored deliverable review, a coaching call, and a "Voice Orb demo record block."
- **[09:28] Voice architecture diagram** — mic → **faster-whisper** (open-source STT) → **Claude Haiku 4.5** (routing brain, swappable for local model) → 3 tiers (skills / metrics / headless `claude -p`) → **Kokoro** (open-source TTS) → spoken reply. `frame_0025.jpg`
- **[12:26] Skills section begins** — workflow to derive skills: (1) stream-of-consciousness voice dump to Claude Code, (2) mine Claude Code's own tool-call logs over 30/60/90 days, (3) combine both; promote a skill to a scheduled automation only after it's proven manually.
- **[16:35] Memory layer / Karpathy tweet** — explicitly cites Andrej Karpathy's viral (~22M views, April) tweet as the template: vault split into `raw/`, `wiki/`, `output/` folders, each with a master `index.md` acting as a table of contents so Claude Code (and the human) can navigate at scale. `frame_0033.jpg`, `frame_0049.jpg`
- **[19:49] Reframe of "memory"** — explicit correction: the Obsidian layer is "not really giving it more memory, it's giving it a map" — the benefit is faster/cheaper navigation, not a graph-RAG-style knowledge store (presenter explicitly denies it's "graph rag").
- **[20:44] Building the plugin** — workflow: describe the desired command center to Claude Code, use Claude (the design tool "Claude design") to generate 5 distinct visual mockup variations from Pinterest-style inspiration screenshots, iterate/refine on a favorite, export the mockup code as a zip, hand it to Claude Code to build and auto-install the actual Obsidian plugin. Mentions the community "Hot Reload" Obsidian plugin (found via GitHub search, not the official plugin browser) as a dev-loop aid.

## Hook microscope (0-10s)

- Frames: 20 at 2 fps

Talking-head, static single shot for the full 0-10s window — no B-roll or screen capture appears until after ~00:40 (once "we've gone through a few iterations" starts). The visual is deliberately static; all the hook weight is carried by the script. Line-by-line: "You are using Claude code in Obsidian the wrong way" (direct-address contrarian claim aimed at the presumed-Obsidian-using viewer) → "or at least you're barely scratching the surface" (softens/broadens the claim so it applies even to advanced users) → "We can use Obsidian to do a lot more than just track markdown files" (reframes Obsidian's category from note-app to OS-substrate) → rapid-fire value list ("fleet of skills and automations, a memory layer, and a visual wrapper... that gives us insights you just can't get with the terminal or desktop app") stacks scope before any payoff is shown → "Did I also mention we can give it fully local voice capabilities?" (a second escalation right as attention would dip) → explicit promise-and-structure line ("that's exactly what we're going to cover today, and by the end of this video you're going to understand how to build this yourself") closes the hook with a concrete deliverable. Pattern: **contrarian claim → category reframe → escalating value stack → explicit promise**, no demo shown yet (demo-first is deferred to ~01:16).

## Editorial profile

- Shots: 80
- Cuts/min: 3.29
- Mean shot length: 18.22s
- Median shot length: 4.03s
- Talking-head ratio: n/a (opencv not installed)

Slow-cut YouTube tutorial style: long dwell shots (median ~4s, but mean pulled to ~18s by extended static-dashboard segments) alternating webcam talking-head with full-screen desktop/Obsidian screen capture; no on-screen text overlays or jump-cut editing — pacing is driven by screen-demo dwell time, not by editorial cutting.

## Quotable moments

- **[00:02]** "You are using Claude code in Obsidian the wrong way, or at least you're barely scratching the surface."
- **[07:41]** "This becomes a visual spectacle if we don't have this foundation." (skills/automations backbone must exist before the dashboard has substance)
- **[08:03]** "It's not like a graph rag at all, actually." (correcting hype around Obsidian-as-memory)
- **[19:49]** "It's not really giving it more memory, it's giving it a map."
- **[13:02]** "One of the issues with AI is that it is inherently non-deterministic... if I can instead specify the way I want things done, and specify an end state, we can then turn that into a skill."

## Entities mentioned

- People: [[chase-ai]] (presenter/channel), [[andrej-karpathy]] (source of the vault-structure tweet referenced repeatedly)
- Companies: [[anthropic]] (Claude, Haiku 4.5), [[openai]] (referenced via ChatGPT/GPT live mode comparison)
- Tools / products: [[claude-code]], [[obsidian]], [[claude-design]] (mockup generation), [[faster-whisper]] (open-source local STT), [[kokoro]] (open-source TTS), [[haiku-4-5]] (routing LLM), [[hot-reload-obsidian-plugin]] (community plugin, GitHub-only distribution), Google Calendar (data source), Codex / ChatGPT voice mode (comparison reference)
- Places: none named

## Concepts surfaced

- **Claude OS / agentic OS**: a personal, self-built stack of Claude Code + a visual command-center UI + codified skills/automations + a navigable memory layer — not a single product, a DIY architecture pattern.
- **Skills-before-automations discipline**: turn a repeated task into a Claude Code skill first, validate its output manually, only then promote it to a scheduled/unattended automation.
- **3-tier voice command routing**: Tier 1 (execute a named skill, no reasoning), Tier 2 (answer from an already-generated report/metric, fast, no fresh research), Tier 3 (spin up a full headless `claude -p` agent run, slowest, catch-all for open-ended requests).
- **Memory-as-map, not memory-as-recall**: Obsidian's value to Claude Code is a navigable folder/index structure that cuts token usage and lookup time — explicitly not a vector/graph-RAG knowledge store.
- **Karpathy vault structure (raw / wiki / output)**: raw findings → synthesized "wiki" articles → derived deliverables, each level with a master `index.md` acting as a table of contents for both human and agent navigation.
- **Design-through-iteration via Claude Design**: generate multiple (5+) distinct visual mockups from reference images, converge on a favorite, iterate variations of it, export as a code zip, hand to Claude Code to build and self-install as a real Obsidian plugin.

## Transcript

_Source: captions._

```
[00:02] You are using Claude code in Obsidian the wrong way, or at least you're barely
[00:05] the wrong way, or at least you're barely scratching the surface. We can use
[00:06] scratching the surface. We can use Obsidian to do a lot more than just
[00:08] Obsidian to do a lot more than just track markdown files for us. Instead, we
[00:11] track markdown files for us. Instead, we can use it to create a command center
[00:13] can use it to create a command center for our entire Claude OS, a system that
[00:15] for our entire Claude OS, a system that includes a fleet of skills and
[00:17] includes a fleet of skills and automations, a memory layer, and a
[00:19] automations, a memory layer, and a visual wrapper on top of it all that
[00:21] visual wrapper on top of it all that gives us insights that you just can't
[00:23] gives us insights that you just can't get with the terminal or the desktop
[00:25] get with the terminal or the desktop app. Did I also mention that we can give
[00:27] app. Did I also mention that we can give it fully local voice capabilities? But
[00:29] it fully local voice capabilities? But how do we do this in a way that actually
[00:31] how do we do this in a way that actually provides value and doesn't evolve into a
[00:33] provides value and doesn't evolve into a zero-substance visual spectacle? Well,
[00:36] zero-substance visual spectacle? Well, that's exactly what we're going to cover
[00:37] that's exactly what we're going to cover today, and by the end of this video,
[00:39] today, and by the end of this video, you're going to understand how to build
[00:41] you're going to understand how to build this yourself. Now, if you follow this
[00:42] this yourself. Now, if you follow this channel for some time, you know that
[00:44] channel for some time, you know that we've gone through a few iterations of
[00:46] we've gone through a few iterations of this Claude OS. Not too long ago, it
[00:48] this Claude OS. Not too long ago, it looked something like this, which was a
[00:50] looked something like this, which was a web-based version. And before that, we
[00:53] web-based version. And before that, we had an Obsidian version. Now, the cool
[00:56] had an Obsidian version. Now, the cool thing with this web-based version we had
[00:57] thing with this web-based version we had was the voice capabilities, a fully
[00:59] was the voice capabilities, a fully local voice setup that allowed us to
[01:01] local voice setup that allowed us to give very quick responses and control
[01:02] give very quick responses and control some things through our microphone.
[01:05] some things through our microphone. Now, what I've done is we've essentially
[01:07] Now, what I've done is we've essentially upgraded the Obsidian command center,
[01:10] upgraded the Obsidian command center, and we've brought in the best parts of
[01:12] and we've brought in the best parts of the web version and combined it into
[01:14] the web version and combined it into what you see here. This gives us all the
[01:16] what you see here. This gives us all the power of Obsidian. I've included a voice
[01:19] power of Obsidian. I've included a voice setup, which was very much inspired by
[01:21] setup, which was very much inspired by what we see from Codex and ChatGPT's
[01:24] what we see from Codex and ChatGPT's voice mode, and we now have a one-stop
[01:26] voice mode, and we now have a one-stop shop for everything we want to do with
[01:28] shop for everything we want to do with Claude code. But what does this whole
[01:30] Claude code. But what does this whole thing actually buy us that we don't get
[01:31] thing actually buy us that we don't get inside the terminal and don't get inside
[01:32] inside the terminal and don't get inside the desktop app? We have to answer that
[01:34] the desktop app? We have to answer that question, or else this whole thing is
[01:36] question, or else this whole thing is kind of pointless. Well, let's start on
[01:37] kind of pointless. Well, let's start on the visual side with what we're actually
[01:39] the visual side with what we're actually looking at. First things first, it gives
[01:40] looking at. First things first, it gives us a simple glance at whatever single
[01:42] us a simple glance at whatever single metric we want. What I really want to
[01:43] metric we want. What I really want to hammer in here is that this is 100%
[01:46] hammer in here is that this is 100% customizable, so whatever you want to be
[01:48] customizable, so whatever you want to be able to see, you can put inside here.
[01:50] able to see, you can put inside here. This is just a custom Obsidian plugin
[01:52] This is just a custom Obsidian plugin that Claude code actually built for me.
[01:54] that Claude code actually built for me. I want some sort of insight on what I'm
[01:55] I want some sort of insight on what I'm doing with my token usage. I can see all
[01:57] doing with my token usage. I can see all of my metrics across social media
[01:59] of my metrics across social media channels. I can see my schedule that is
[02:01] channels. I can see my schedule that is pulled from my Google Calendar. From
[02:03] pulled from my Google Calendar. From that, it breaks down specific tasks for
[02:05] that, it breaks down specific tasks for me, and then I also get some insight in
[02:07] me, and then I also get some insight in terms of my morning headlines.
[02:09] terms of my morning headlines. Right here, you can see different
[02:10] Right here, you can see different automations and skills that I can run at
[02:12] automations and skills that I can run at a click of the button, and I have
[02:14] a click of the button, and I have different tabs here that dive deeper
[02:17] different tabs here that dive deeper into these different reports that I run
[02:18] into these different reports that I run daily. For example, this is my research
[02:21] daily. For example, this is my research report. This comes from a morning intel
[02:23] report. This comes from a morning intel automation, which gives me all the
[02:25] automation, which gives me all the GitHub trending repos based on the last
[02:27] GitHub trending repos based on the last 7 days, last 30 days, and then I can
[02:29] 7 days, last 30 days, and then I can also see outlier videos on YouTube,
[02:32] also see outlier videos on YouTube, different content angles, and then I get
[02:33] different content angles, and then I get sort of a running look at what's
[02:35] sort of a running look at what's trending on Hacker News. When I look at
[02:37] trending on Hacker News. When I look at my audience tab, this is taking a look
[02:39] my audience tab, this is taking a look at how my specific content is doing
[02:41] at how my specific content is doing across YouTube, what's working, what
[02:43] across YouTube, what's working, what isn't, and why. And since this is
[02:44] isn't, and why. And since this is Obsidian, I'm not limited just to this.
[02:46] Obsidian, I'm not limited just to this. I can use the terminal inside of
[02:48] I can use the terminal inside of Obsidian. And this is partly why I like
[02:50] Obsidian. And this is partly why I like this voice mode, cuz I can pull this up
[02:52] this voice mode, cuz I can pull this up at any time and say something like
[02:54] at any time and say something like pull up the terminal.
[03:00] And cool, there it is. Now, this thing does have actual voice stuff. So, if I
[03:02] does have actual voice stuff. So, if I say something like hey, what was the
[03:04] say something like hey, what was the biggest AI news story for today?
[03:12] &gt;&gt; Claude got a model level watermark rolled out globally yesterday.
[03:14] rolled out globally yesterday. Invisible, survives copy/paste,
[03:17] Invisible, survives copy/paste, triggered by the EU AI Act. Deep Seek
[03:20] triggered by the EU AI Act. Deep Seek Harness also exploded to 109k stars in 2
[03:24] Harness also exploded to 109k stars in 2 days and is dominating GitHub trending.
[03:29] days and is dominating GitHub trending. &gt;&gt; So, that's kind of cool that I can like
[03:31] &gt;&gt; So, that's kind of cool that I can like ask it A to do commands inside of
[03:33] ask it A to do commands inside of Obsidian, like I said, pull up my
[03:34] Obsidian, like I said, pull up my terminal or whatever, and I can ask it
[03:36] terminal or whatever, and I can ask it questions about reports I've already
[03:38] questions about reports I've already run. That's why it was relatively quick.
[03:40] run. That's why it was relatively quick. It didn't have to like take my command,
[03:42] It didn't have to like take my command, go out on the web, find that
[03:43] go out on the web, find that information, process it, and then
[03:45] information, process it, and then respond. It's been wired to look at
[03:47] respond. It's been wired to look at these reports that I've already run.
[03:49] these reports that I've already run. Again, something like my research
[03:50] Again, something like my research report, and then quickly answer
[03:51] report, and then quickly answer questions about it. The other cool thing
[03:53] questions about it. The other cool thing about voice mode is this works even when
[03:54] about voice mode is this works even when I'm not inside Obsidian. So, let's say
[03:56] I'm not inside Obsidian. So, let's say I'm tabbed out, I'm doing some other
[03:57] I'm tabbed out, I'm doing some other work elsewhere, like for example, I'm
[03:59] work elsewhere, like for example, I'm inside the Claude desktop app, yet I
[04:01] inside the Claude desktop app, yet I want to ask it a question about
[04:02] want to ask it a question about something. I essentially want to call on
[04:04] something. I essentially want to call on Claude to audibly talk to me. Again,
[04:06] Claude to audibly talk to me. Again, very similar to what we do with GPT live
[04:09] very similar to what we do with GPT live mode, which you can do inside of Codex.
[04:10] mode, which you can do inside of Codex. This is a really good tool. So, in this
[04:12] This is a really good tool. So, in this case, I just hit the hot key
[04:15] case, I just hit the hot key and I can ask something like, "What's
[04:16] and I can ask something like, "What's the biggest thing on my schedule for
[04:17] the biggest thing on my schedule for today?"
[04:26] &gt;&gt; Your biggest commitment today is the sponsored deliverable review for Warp at
[04:28] sponsored deliverable review for Warp at 11:00 a.m. Then the Chase AI plus
[04:31] 11:00 a.m. Then the Chase AI plus coaching call at 3:00 p.m. But the whole
[04:34] coaching call at 3:00 p.m. But the whole day is really built around the Voice Orb
[04:36] day is really built around the Voice Orb demo record block at 9:30, which is the
[04:40] demo record block at 9:30, which is the main focus.
[04:42] main focus. &gt;&gt; And so, like you see there, I'm able to
[04:44] &gt;&gt; And so, like you see there, I'm able to ask questions about different things and
[04:47] ask questions about different things and it can quickly respond. Now, this also,
[04:49] it can quickly respond. Now, this also, this sort of voice mode thing, it
[04:51] this sort of voice mode thing, it doesn't just answer questions about, you
[04:53] doesn't just answer questions about, you know, reports I have going on. It can
[04:55] know, reports I have going on. It can actually call on Claude in the
[04:57] actually call on Claude in the background and run a headless version of
[04:58] background and run a headless version of it. So, if I was doing something else
[05:01] it. So, if I was doing something else and then I actually wanted Claude Code
[05:02] and then I actually wanted Claude Code to go ahead and do something like
[05:04] to go ahead and do something like relatively deep, like, "Hey, go ahead
[05:06] relatively deep, like, "Hey, go ahead and start, you know, planning this
[05:08] and start, you know, planning this project or start, you know, doing deep
[05:10] project or start, you know, doing deep research on X, Y, and Z." It would go
[05:12] research on X, Y, and Z." It would go ahead and do that. It would do it in a
[05:13] ahead and do that. It would do it in a headless mode. Now, the voice response
[05:14] headless mode. Now, the voice response wouldn't be as quick because it has to,
[05:16] wouldn't be as quick because it has to, you know, actually go and do it and then
[05:18] you know, actually go and do it and then respond. But for these quick tasks that
[05:20] respond. But for these quick tasks that are pulling on information I've already
[05:22] are pulling on information I've already found, it's relatively smooth. And
[05:24] found, it's relatively smooth. And again, this is all local. This is a
[05:26] again, this is all local. This is a local voice mode running on my GPU and
[05:28] local voice mode running on my GPU and I'll show you kind of how it's set up.
[05:30] I'll show you kind of how it's set up. But overall, I think in terms of the
[05:32] But overall, I think in terms of the visual page, that's
[05:34] visual page, that's sort of the value this sort of like
[05:35] sort of the value this sort of like wrapper OS Obsidian setup is bringing
[05:38] wrapper OS Obsidian setup is bringing you, which I think is pretty cool,
[05:39] you, which I think is pretty cool, especially the voice mode when it's
[05:40] especially the voice mode when it's tabbed out. Because being able to
[05:41] tabbed out. Because being able to audibly interact with Claude Code even
[05:43] audibly interact with Claude Code even when you're tabbed out and stuff, in a
[05:44] when you're tabbed out and stuff, in a way that is similar again to that GPT
[05:46] way that is similar again to that GPT voice mode, is something I wanted to
[05:47] voice mode, is something I wanted to bring over, cuz the voice mode inside of
[05:49] bring over, cuz the voice mode inside of like the Cloud Desktop app just isn't
[05:51] like the Cloud Desktop app just isn't really there. So, that's what the user
[05:52] really there. So, that's what the user interface and voice mode is actually
[05:54] interface and voice mode is actually bringing to the table. The second thing
[05:56] bringing to the table. The second thing that's actually providing value in a
[05:57] that's actually providing value in a Cloud OS setup is that skill and
[05:59] Cloud OS setup is that skill and automation backbone. You see all these
[06:02] automation backbone. You see all these skills right here that have been, you
[06:04] skills right here that have been, you know, essentially moved into buttons
[06:06] know, essentially moved into buttons that I can click at any one time or I
[06:07] that I can click at any one time or I can never run it being voice mode, and
[06:08] can never run it being voice mode, and that's great. The real value is that I
[06:10] that's great. The real value is that I have taken everything I do in my
[06:12] have taken everything I do in my day-to-day and I have turned them into
[06:14] day-to-day and I have turned them into skills and automations, which is simple
[06:15] skills and automations, which is simple enough concept, but very few people do
[06:17] enough concept, but very few people do it correctly. What you're looking at
[06:18] it correctly. What you're looking at here is a visualization of all the
[06:20] here is a visualization of all the skills and automations I run, and the
[06:22] skills and automations I run, and the concept is relatively simple. You have a
[06:25] concept is relatively simple. You have a number of tasks that you run on a
[06:28] number of tasks that you run on a day-to-day and week-to-week basis, both
[06:30] day-to-day and week-to-week basis, both personally and with your job. These
[06:32] personally and with your job. These tasks are broken out into different
[06:34] tasks are broken out into different domains. For me, that includes things
[06:36] domains. For me, that includes things like memory, productivity, research,
[06:39] like memory, productivity, research, content, my community, my agency, sales,
[06:41] content, my community, my agency, sales, so on and so forth.
[06:43] so on and so forth. Within each of these domains, there's
[06:45] Within each of these domains, there's specific things that I do. For research,
[06:47] specific things that I do. For research, for example, I have a pipeline dedicated
[06:49] for example, I have a pipeline dedicated to YouTube. I deep research specific
[06:51] to YouTube. I deep research specific topics. I have stuff that goes into my
[06:53] topics. I have stuff that goes into my light rag database. I have my morning
[06:55] light rag database. I have my morning trend scan, which is essentially that
[06:56] trend scan, which is essentially that report you saw earlier. I want to be
[06:58] report you saw earlier. I want to be able to look at my competitors, etc.,
[06:59] able to look at my competitors, etc., etc., etc.
[07:01] etc., etc. I could do all these manually or, after
[07:03] I could do all these manually or, after I figured out how I actually wanted to
[07:05] I figured out how I actually wanted to work manually, I turn them into skills.
[07:07] work manually, I turn them into skills. And then once they've been turned into
[07:08] And then once they've been turned into skills, I ask myself, "Does it make
[07:10] skills, I ask myself, "Does it make sense for this to be an automation?" If
[07:12] sense for this to be an automation?" If yes, that's what I do. Now, doing this
[07:14] yes, that's what I do. Now, doing this has nothing to really do with like a
[07:16] has nothing to really do with like a Cloud OS and the Obsidian dashboard you
[07:17] Cloud OS and the Obsidian dashboard you said. This is just like best practice
[07:19] said. This is just like best practice every everyone should be doing.
[07:21] every everyone should be doing. However, building this
[07:23] However, building this is
[07:24] is what essentially is the foundation of
[07:27] what essentially is the foundation of the Cloud OS. If you don't have this,
[07:28] the Cloud OS. If you don't have this, creating something like this is kind of
[07:30] creating something like this is kind of pointless. Like, what are we even doing
[07:31] pointless. Like, what are we even doing here? There's no like information that's
[07:33] here? There's no like information that's going to travel here. You're not going
[07:34] going to travel here. You're not going to be able to call on specific skills
[07:35] to be able to call on specific skills and automations regularly. This becomes
[07:38] and automations regularly. This becomes a visual spectacle if we don't have this
[07:41] a visual spectacle if we don't have this foundation. So, this is the actual
[07:43] foundation. So, this is the actual substance and we'll go into the best
[07:44] substance and we'll go into the best practices of creating something like
[07:46] practices of creating something like this for yourself cuz it's not really
[07:47] this for yourself cuz it's not really hard. And then last but not least, we
[07:49] hard. And then last but not least, we have sort of the Obsidian memory layer,
[07:51] have sort of the Obsidian memory layer, which I think people get confused with.
[07:53] which I think people get confused with. The whole point of the Obsidian memory
[07:55] The whole point of the Obsidian memory layer isn't that it's necessarily
[07:57] layer isn't that it's necessarily supercharging Claude code. Like we see
[08:00] supercharging Claude code. Like we see all the stuff and we get like super
[08:01] all the stuff and we get like super hyped up about, "Oh my gosh, look at
[08:03] hyped up about, "Oh my gosh, look at like this graph. This looks super cool.
[08:04] like this graph. This looks super cool. It's like a graph rag." Like it's not
[08:06] It's like a graph rag." Like it's not like a graph rag. It's not like graph
[08:07] like a graph rag. It's not like graph rag at all, actually. What Obsidian does
[08:09] rag at all, actually. What Obsidian does is it organizes information in markdown
[08:12] is it organizes information in markdown files for you, the human. And there is a
[08:14] files for you, the human. And there is a small tangential benefit for Claude code
[08:17] small tangential benefit for Claude code itself. That tangential benefit for
[08:19] itself. That tangential benefit for Claude code comes into effect when we
[08:21] Claude code comes into effect when we have
[08:22] have thousands of files and we have set up
[08:24] thousands of files and we have set up our Obsidian vault in a way that
[08:26] our Obsidian vault in a way that actually makes sense. It makes it easy
[08:27] actually makes sense. It makes it easy for Claude code to navigate to give us
[08:29] for Claude code to navigate to give us accurate answers quickly. It essentially
[08:31] accurate answers quickly. It essentially saves us on tokens and boosts the
[08:32] saves us on tokens and boosts the performance a little bit. And that is
[08:34] performance a little bit. And that is entirely a result of how you set it up.
[08:36] entirely a result of how you set it up. What you see here is that Karpathy
[08:38] What you see here is that Karpathy Obsidian rag system you see everywhere
[08:40] Obsidian rag system you see everywhere and this is sort of the template for it.
[08:42] and this is sort of the template for it. And again, we'll go into deeper detail
[08:44] And again, we'll go into deeper detail of how you would set it up cuz you don't
[08:45] of how you would set it up cuz you don't have to do it exactly like Karpathy did,
[08:47] have to do it exactly like Karpathy did, but there are some fundamentals we can
[08:49] but there are some fundamentals we can pull from it. So, that's what this
[08:51] pull from it. So, that's what this Obsidian plus Claude OS does. That's
[08:53] Obsidian plus Claude OS does. That's what it buys you and what you can't get
[08:54] what it buys you and what you can't get inside the terminal or inside the
[08:57] inside the terminal or inside the desktop app. And now let's talk about
[08:59] desktop app. And now let's talk about how you would actually create this for
[09:00] how you would actually create this for yourself.
[09:02] yourself. But first, a quick word from today's
[09:04] But first, a quick word from today's sponsor, me. So, I just released a brand
[09:06] sponsor, me. So, I just released a brand new version of my Claude code
[09:07] new version of my Claude code masterclass and it's the number one way
[09:09] masterclass and it's the number one way to master this tool, especially if you
[09:11] to master this tool, especially if you don't come from a technical background.
[09:13] don't come from a technical background. We focus on real practical use cases so
[09:15] We focus on real practical use cases so you can actually learn the fundamentals
[09:17] you can actually learn the fundamentals and then turn around and apply this to
[09:19] and then turn around and apply this to whatever personal project you want.
[09:21] whatever personal project you want. We're currently running a sale on the
[09:23] We're currently running a sale on the membership, so if you want to join,
[09:25] membership, so if you want to join, check the link in the pinned comment.
[09:26] check the link in the pinned comment. You can find it inside of Chase AI Plus.
[09:28] You can find it inside of Chase AI Plus. Now before I explain how to create your
[09:30] Now before I explain how to create your own skill and automation backbone for
[09:32] own skill and automation backbone for your Claude OS, let me walk you through
[09:34] your Claude OS, let me walk you through the voice setup so you sort of
[09:36] the voice setup so you sort of understand how it's actually working.
[09:38] understand how it's actually working. So, in this example, you are saying,
[09:41] So, in this example, you are saying, "Hey, what's today's biggest AI news?"
[09:45] "Hey, what's today's biggest AI news?" This voice command goes to the voice
[09:48] This voice command goes to the voice module, call it Jarvis, whatever you
[09:50] module, call it Jarvis, whatever you want, and that voice recording is then
[09:53] want, and that voice recording is then transcribed via faster Whisper, which is
[09:56] transcribed via faster Whisper, which is a open-source repo. It's going to live
[09:58] a open-source repo. It's going to live on your computer, does a transcription.
[10:00] on your computer, does a transcription. From there, your voice got turned into
[10:01] From there, your voice got turned into words, and those words get sent to Haiku
[10:04] words, and those words get sent to Haiku 4.5. I used Haiku because it's the
[10:07] 4.5. I used Haiku because it's the smallest, cheapest, fastest model. We
[10:09] smallest, cheapest, fastest model. We also have the ability, if you want, to
[10:11] also have the ability, if you want, to swap out Haiku for any sort of local
[10:13] swap out Haiku for any sort of local model. The reason I don't have the local
[10:15] model. The reason I don't have the local setup is because
[10:17] setup is because I give this exact setup away to people.
[10:19] I give this exact setup away to people. You can find it inside of Chase AI Plus.
[10:21] You can find it inside of Chase AI Plus. And I don't know necessarily what their
[10:22] And I don't know necessarily what their hardware is going to be. So, the power
[10:25] hardware is going to be. So, the power of their local model can change a lot.
[10:26] of their local model can change a lot. So, Haiku's like a nice standard. But,
[10:28] So, Haiku's like a nice standard. But, if you have the hardware for it, you
[10:29] if you have the hardware for it, you could change this for really whatever
[10:30] could change this for really whatever you want. Throw in Klein, throw in
[10:32] you want. Throw in Klein, throw in whatever.
[10:33] whatever. So,
[10:34] So, what's the biggest AI news? It becomes
[10:35] what's the biggest AI news? It becomes text. That text goes to Haiku, and Haiku
[10:37] text. That text goes to Haiku, and Haiku now figures out where to route this. And
[10:39] now figures out where to route this. And there's really three tiers this is
[10:41] there's really three tiers this is broken into.
[10:42] broken into. So, tier one is skills. If I told, you
[10:45] So, tier one is skills. If I told, you know, Jarvis, "Hey, I want you to run
[10:47] know, Jarvis, "Hey, I want you to run the morning intel report." Well, that's
[10:49] the morning intel report." Well, that's going to get routed to tier one, and it
[10:50] going to get routed to tier one, and it knows it's just going to have to execute
[10:52] knows it's just going to have to execute a skill. Doesn't have to add any other
[10:54] a skill. Doesn't have to add any other words to it. Just execute the skill.
[10:55] words to it. Just execute the skill. Just do what you're told, right? And
[10:56] Just do what you're told, right? And then let me know when it's done.
[10:59] then let me know when it's done. Tier two is, "Hey, I just want you to
[11:00] Tier two is, "Hey, I just want you to pull metrics." So, that's what we're
[11:02] pull metrics." So, that's what we're asking here. I'm saying, "What's today's
[11:03] asking here. I'm saying, "What's today's biggest AI news?" I want it to just look
[11:05] biggest AI news?" I want it to just look at a report that already exists. So, if
[11:07] at a report that already exists. So, if I'm asking about news, it knows it can
[11:09] I'm asking about news, it knows it can go to essentially the research tab, take
[11:11] go to essentially the research tab, take a look at our morning intel report, and
[11:13] a look at our morning intel report, and let me know these things. We break out
[11:15] let me know these things. We break out this specific tier because we want this
[11:16] this specific tier because we want this to be fast. I don't want it to do any
[11:18] to be fast. I don't want it to do any like searching or research on its own.
[11:19] like searching or research on its own. Just find whatever exists and tell me.
[11:21] Just find whatever exists and tell me. So, that would be what this command
[11:23] So, that would be what this command goes. Goes into tier two. Then we have
[11:24] goes. Goes into tier two. Then we have tier three, and I alluded to this
[11:25] tier three, and I alluded to this earlier. If I pull a voice mode, and I
[11:27] earlier. If I pull a voice mode, and I say, "Hey, I want you to go ahead, pull
[11:28] say, "Hey, I want you to go ahead, pull up Fable 5. I want you to start doing
[11:30] up Fable 5. I want you to start doing deep research on task X, Y, and Z, and
[11:32] deep research on task X, Y, and Z, and then coming up with a plan for action.
[11:34] then coming up with a plan for action. Well, that isn't a specific skill, and
[11:36] Well, that isn't a specific skill, and that's not a metric. We need to actually
[11:38] that's not a metric. We need to actually like pull up an actual instance of
[11:40] like pull up an actual instance of Claude code, and that's what this is
[11:41] Claude code, and that's what this is going to do. It's going to do it
[11:42] going to do. It's going to do it completely headlessly, it's going to run
[11:44] completely headlessly, it's going to run all the things, and then it's going to
[11:45] all the things, and then it's going to report when it's done. So, this becomes
[11:47] report when it's done. So, this becomes kind of the catch-all. This requires the
[11:48] kind of the catch-all. This requires the most power, and obviously it's going to
[11:49] most power, and obviously it's going to be the slowest.
[11:50] be the slowest. Now, once it executes any of these
[11:52] Now, once it executes any of these tasks, whether it's in tier one, two, or
[11:54] tasks, whether it's in tier one, two, or three, it's obviously the response is
[11:56] three, it's obviously the response is going to be in text, but we want that to
[11:58] going to be in text, but we want that to be a voice response. So, that is where
[12:01] be a voice response. So, that is where Kakora comes in, again an open-source
[12:03] Kakora comes in, again an open-source tool, which then gets sent back up to
[12:05] tool, which then gets sent back up to here, and then it responds to us with,
[12:08] here, and then it responds to us with, you know, whatever it's going to say.
[12:10] you know, whatever it's going to say. So, that's how the voice mode works. You
[12:12] So, that's how the voice mode works. You say a command, it gets transcribed, it
[12:14] say a command, it gets transcribed, it gets routed, command is executed, turned
[12:17] gets routed, command is executed, turned into a voice, sent back up. And it's
[12:19] into a voice, sent back up. And it's actually simple enough, and like I said,
[12:20] actually simple enough, and like I said, you could turn this 100% local if you
[12:22] you could turn this 100% local if you wanted to by simply swapping out Haiku
[12:25] wanted to by simply swapping out Haiku for your local model of choice. Now,
[12:27] for your local model of choice. Now, let's talk about the skills. I have some
[12:29] let's talk about the skills. I have some of my most commonly used ones right
[12:30] of my most commonly used ones right here, so at any time I want to run them,
[12:32] here, so at any time I want to run them, and I have this tab open, I can just
[12:34] and I have this tab open, I can just click on them. And like you saw as we
[12:35] click on them. And like you saw as we went through the voice mode, we can
[12:37] went through the voice mode, we can easily trigger them just by saying the
[12:39] easily trigger them just by saying the name through the voice system. Don't
[12:41] name through the voice system. Don't even have to be tabbed in. But the
[12:42] even have to be tabbed in. But the question becomes, how do we actually
[12:44] question becomes, how do we actually create these skills, and what should
[12:45] create these skills, and what should those skills look like? Luckily, as
[12:47] those skills look like? Luckily, as complicated this looks, the workflow for
[12:49] complicated this looks, the workflow for doing this is actually pretty simple.
[12:51] doing this is actually pretty simple. Step one is defining the tasks. What is
[12:55] Step one is defining the tasks. What is it you actually do in your day-to-day
[12:57] it you actually do in your day-to-day that we can codify? Remember, one of the
[12:59] that we can codify? Remember, one of the issues with AI is that it is inherently
[13:02] issues with AI is that it is inherently non-deterministic. I tell it to do one
[13:04] non-deterministic. I tell it to do one thing, and I tell it to do that one
[13:05] thing, and I tell it to do that one thing 10 different times, it's going to
[13:07] thing 10 different times, it's going to go about it 10 different ways. If I can
[13:09] go about it 10 different ways. If I can instead specify the way I want things
[13:12] instead specify the way I want things done, and specify an end state, we can
[13:14] done, and specify an end state, we can then turn that into a skill, and
[13:15] then turn that into a skill, and essentially codify it, make it as
[13:17] essentially codify it, make it as deterministic as possible.
[13:19] deterministic as possible. But we have to know what those tasks
[13:20] But we have to know what those tasks even are. So, the way we can do that is,
[13:23] even are. So, the way we can do that is, well, luckily we actually have a few
[13:24] well, luckily we actually have a few options to do this.
[13:25] options to do this. The first option is we just kind of give
[13:27] The first option is we just kind of give it a stream of consciousness. All right,
[13:30] it a stream of consciousness. All right, you're going to turn on your microphone
[13:32] you're going to turn on your microphone and you are just going to yap to Claude
[13:36] and you are just going to yap to Claude Code and explain what you do every day
[13:38] Code and explain what you do every day and what you do every week. Based on
[13:40] and what you do every week. Based on that conversation, we're then going to
[13:41] that conversation, we're then going to ask Claude Code, "Hey,
[13:43] ask Claude Code, "Hey, I just gave you a bunch of information
[13:45] I just gave you a bunch of information about what I do. Which parts of that can
[13:47] about what I do. Which parts of that can we turn into skills?" And then it turns
[13:48] we turn into skills?" And then it turns them into skills for you. The second way
[13:50] them into skills for you. The second way to do this is you have it take a look at
[13:52] to do this is you have it take a look at your actual logs. Everything you do
[13:55] your actual logs. Everything you do inside of Claude Code, every single tool
[13:57] inside of Claude Code, every single tool call, every single command, every single
[13:59] call, every single command, every single text is logged on your computer. We can
[14:02] text is logged on your computer. We can have Claude Code take a look at these
[14:03] have Claude Code take a look at these logs over the last 30, 60, 90 days and
[14:06] logs over the last 30, 60, 90 days and then pull skills out of that. This is
[14:08] then pull skills out of that. This is really nice because we have an idea in
[14:10] really nice because we have an idea in our mind, right, about what it is we
[14:12] our mind, right, about what it is we actually do,
[14:13] actually do, but what is the reality of that, right?
[14:16] but what is the reality of that, right? What do you literally use Claude Code
[14:18] What do you literally use Claude Code for? We're going to be able to see this
[14:19] for? We're going to be able to see this in the logs. And ideally, you'd actually
[14:21] in the logs. And ideally, you'd actually do step number three, which is a combo
[14:23] do step number three, which is a combo of both of these things, right? You do
[14:24] of both of these things, right? You do the stream of consciousness, you tell
[14:25] the stream of consciousness, you tell Claude Code what it you think it is you
[14:27] Claude Code what it you think it is you actually do, and it creates skills from
[14:29] actually do, and it creates skills from that. Then we take a look at the logs
[14:31] that. Then we take a look at the logs themselves
[14:33] themselves and pull that out and in combination
[14:35] and pull that out and in combination with those two things, you begin to
[14:37] with those two things, you begin to build this repertoire of skills. Now,
[14:40] build this repertoire of skills. Now, which skills do we turn into
[14:42] which skills do we turn into automations? Often times, that's going
[14:44] automations? Often times, that's going to be pretty self-evident, right? Is
[14:46] to be pretty self-evident, right? Is this something you need to run every
[14:47] this something you need to run every single day at a specific time? Well,
[14:49] single day at a specific time? Well, then turn it into an automation, turn it
[14:51] then turn it into an automation, turn it into routine, which is one command away.
[14:53] into routine, which is one command away. You just tell Claude Code to do it for
[14:55] You just tell Claude Code to do it for you. Now, when it comes to automations
[14:57] you. Now, when it comes to automations and skills, really the best practice is
[14:59] and skills, really the best practice is to keep it as a skill first for a while,
[15:01] to keep it as a skill first for a while, actually make sure this is working the
[15:02] actually make sure this is working the way and the manner you want, and then
[15:04] way and the manner you want, and then once you're happy with the outputs
[15:05] once you're happy with the outputs you're getting with the skills, then we
[15:07] you're getting with the skills, then we go ahead and turn it into a full-blown
[15:08] go ahead and turn it into a full-blown automation that we don't run manually,
[15:10] automation that we don't run manually, it just does its thing.
[15:12] it just does its thing. And we can go even deeper with this, and
[15:14] And we can go even deeper with this, and I'm not going to do that in this lesson
[15:16] I'm not going to do that in this lesson and essentially start adding some like
[15:17] and essentially start adding some like loop engineering principles where we're
[15:19] loop engineering principles where we're taking a look at these automations and
[15:21] taking a look at these automations and and that run, we compare them with their
[15:24] and that run, we compare them with their past outputs, and we build some sort of
[15:26] past outputs, and we build some sort of system where it becomes self-improving,
[15:28] system where it becomes self-improving, right? We give it some sort of specific
[15:29] right? We give it some sort of specific goal, some sort of criteria trying to
[15:31] goal, some sort of criteria trying to hit, and if that automation doesn't hit
[15:32] hit, and if that automation doesn't hit it, we can continue to adjust. But,
[15:34] it, we can continue to adjust. But, that's a little more advanced. Just
[15:35] that's a little more advanced. Just understand that's where you can go with
[15:37] understand that's where you can go with this.
[15:38] this. But, it's all built upon the skills.
[15:40] But, it's all built upon the skills. Right? Can we codify what you do every
[15:42] Right? Can we codify what you do every day into a skill? The answer is yes, and
[15:45] day into a skill? The answer is yes, and it is simple. From there, integrating
[15:47] it is simple. From there, integrating that into your Claude OS is really just
[15:48] that into your Claude OS is really just as simple as this. Like, which ones do
[15:50] as simple as this. Like, which ones do you use
[15:51] you use daily?
[15:52] daily? And in terms of the voice mode section,
[15:54] And in terms of the voice mode section, it already knows what skills exist. So,
[15:55] it already knows what skills exist. So, there's nothing you really even have to
[15:57] there's nothing you really even have to do there. Remember, like it's Haiku,
[15:58] do there. Remember, like it's Haiku, it's Claude, it has a list of everything
[16:00] it's Claude, it has a list of everything you do
[16:01] you do in the background. And those skills are
[16:02] in the background. And those skills are also going to form the basis of what
[16:04] also going to form the basis of what your command center even looks like
[16:05] your command center even looks like here, right? Everything you see here is
[16:06] here, right? Everything you see here is essentially some sort of skill or some
[16:08] essentially some sort of skill or some sort of automation, whether it's pulling
[16:10] sort of automation, whether it's pulling my schedule from Google, whether it's
[16:12] my schedule from Google, whether it's the morning headlines, whether it's
[16:13] the morning headlines, whether it's pulling metrics from social media,
[16:15] pulling metrics from social media, whether it's this research section. This
[16:17] whether it's this research section. This is all just outputs and data from
[16:19] is all just outputs and data from automations.
[16:21] automations. That's all this is. Now, yours is going
[16:23] That's all this is. Now, yours is going to look different, and that's a good
[16:24] to look different, and that's a good thing. That's why I think the system is
[16:26] thing. That's why I think the system is great because it is fully customizable.
[16:28] great because it is fully customizable. Whatever it is you want to see should be
[16:31] Whatever it is you want to see should be an output of a skill, and then we throw
[16:33] an output of a skill, and then we throw it on here. And boom, it's yours. Now,
[16:36] it on here. And boom, it's yours. Now, let's talk about the memory side of the
[16:37] let's talk about the memory side of the equation and what Obsidian actually
[16:39] equation and what Obsidian actually brings to the table in terms of {quote}
[16:40] brings to the table in terms of {quote} improving Claude's memory. Now, this is
[16:43] improving Claude's memory. Now, this is the tweet from Karpathy that made
[16:44] the tweet from Karpathy that made everyone lose their minds over Obsidian
[16:47] everyone lose their minds over Obsidian and sort of that Claude code connection.
[16:48] and sort of that Claude code connection. Like, this is out in April, nearly 22
[16:51] Like, this is out in April, nearly 22 million views, and sort of the system he
[16:53] million views, and sort of the system he laid out is relatively simple. And this
[16:55] laid out is relatively simple. And this is what it looks like. Our Obsidian
[16:57] is what it looks like. Our Obsidian command center, our Claude OS, primarily
[16:59] command center, our Claude OS, primarily lives in a folder known as the vault.
[17:02] lives in a folder known as the vault. Doesn't literally have to be called the
[17:03] Doesn't literally have to be called the vault, but that's sort of the naming
[17:05] vault, but that's sort of the naming conventions that Obsidian uses. It's
[17:06] conventions that Obsidian uses. It's just a folder on your computer.
[17:08] just a folder on your computer. Within that folder, we have three
[17:11] Within that folder, we have three subfolders. We have raw,
[17:13] subfolders. We have raw, we have wiki, and And have output. So, I
[17:17] we have wiki, and And have output. So, I want you to imagine we have Claude open
[17:20] want you to imagine we have Claude open up in this vault folder and we say, "I
[17:22] up in this vault folder and we say, "I want you to do some research on rag
[17:26] want you to do some research on rag systems." So, it goes out and it finds a
[17:28] systems." So, it goes out and it finds a bunch of data, a bunch of sources, a
[17:31] bunch of data, a bunch of sources, a bunch of raw information about AI
[17:33] bunch of raw information about AI agents. All that raw data is essentially
[17:36] agents. All that raw data is essentially put inside the raw folder and lives
[17:37] put inside the raw folder and lives here, right? We have article about rag.
[17:40] here, right? We have article about rag. Now, let's say you want to go a step
[17:43] Now, let's say you want to go a step further and you want to take all that
[17:45] further and you want to take all that raw information and you want to turn it
[17:46] raw information and you want to turn it into like a Wikipedia-style article.
[17:48] into like a Wikipedia-style article. Well, that thing goes into the wiki
[17:50] Well, that thing goes into the wiki section. And you can see here we have a
[17:53] section. And you can see here we have a subfolder in the wiki section for rag
[17:55] subfolder in the wiki section for rag systems.
[17:56] systems. So, all that data gets turned into a new
[17:58] So, all that data gets turned into a new article about vector databases and we
[18:01] article about vector databases and we have a second article that has to do
[18:03] have a second article that has to do with chunking strategies. Right? We're
[18:05] with chunking strategies. Right? We're essentially just synthesizing all that
[18:06] essentially just synthesizing all that raw information we found. Now, let's say
[18:08] raw information we found. Now, let's say we want to turn that into a slide deck.
[18:10] we want to turn that into a slide deck. I want a slide deck talking about rag
[18:12] I want a slide deck talking about rag systems. Well, then that slide deck is
[18:14] systems. Well, then that slide deck is going to get put into the output folder.
[18:17] going to get put into the output folder. Right? We're turning into an actual
[18:17] Right? We're turning into an actual deliverable and it is now a slide deck.
[18:20] deliverable and it is now a slide deck. So,
[18:21] So, the simple idea is we have a section for
[18:23] the simple idea is we have a section for raw information, we have a section for
[18:25] raw information, we have a section for sort of just like synthesized data, and
[18:27] sort of just like synthesized data, and then we have the deliverables we create
[18:29] then we have the deliverables we create from the synthesized data.
[18:31] from the synthesized data. Now, the important thing here isn't that
[18:33] Now, the important thing here isn't that we have that sort of, you know,
[18:35] we have that sort of, you know, breakdown. It's that it gives AI a clear
[18:38] breakdown. It's that it gives AI a clear path forward to find information. And
[18:41] path forward to find information. And the way it does it isn't just because we
[18:42] the way it does it isn't just because we have the folders, it's because at every
[18:44] have the folders, it's because at every step of the way we have essentially a
[18:47] step of the way we have essentially a master index or an index.markdown file,
[18:50] master index or an index.markdown file, which acts as a table of contents that
[18:52] which acts as a table of contents that says, "Hey,
[18:53] says, "Hey, once you go into the wiki folder, you
[18:55] once you go into the wiki folder, you can now read this markdown file that
[18:56] can now read this markdown file that says, 'Here's the three subfolders
[18:58] says, 'Here's the three subfolders inside here. We have folders for AI
[19:00] inside here. We have folders for AI agents, rag systems, and content
[19:01] agents, rag systems, and content creation.'"
[19:02] creation.'" Does AI need a master index a table of
[19:05] Does AI need a master index a table of contents when you have three subfolders?
[19:06] contents when you have three subfolders? Absolutely not. But, what if you have
[19:07] Absolutely not. But, what if you have 3,000? What if you have 30,000? What if
[19:10] 3,000? What if you have 30,000? What if you have 3 million? Right? It becomes a
[19:12] you have 3 million? Right? It becomes a little bit easier for everyone involved
[19:13] little bit easier for everyone involved if there is a table of contents, and
[19:15] if there is a table of contents, and that idea is repeated as we go one layer
[19:17] that idea is repeated as we go one layer deep. So, I went to a wiki, I saw the
[19:20] deep. So, I went to a wiki, I saw the master index, I wanted to learn about
[19:22] master index, I wanted to learn about rag systems. Well, I go into the side of
[19:24] rag systems. Well, I go into the side of the rag systems. What do I want to learn
[19:25] the rag systems. What do I want to learn about rag systems? Well, guess what?
[19:27] about rag systems? Well, guess what? There's another index file in here that
[19:28] There's another index file in here that says, "Hey, vector databases, chunking
[19:30] says, "Hey, vector databases, chunking strategies, etc."
[19:32] strategies, etc." And the whole point of this is
[19:34] And the whole point of this is is There's really two points. One, for
[19:36] is There's really two points. One, for you, if you the human being wants to be
[19:37] you, if you the human being wants to be able to find stuff, it's pretty easy.
[19:39] able to find stuff, it's pretty easy. Two, there's a clear path. We give
[19:41] Two, there's a clear path. We give Claude code a map to find things. And
[19:43] Claude code a map to find things. And because it has that map, it gives us
[19:45] because it has that map, it gives us answers quicker, and it's going to burn
[19:46] answers quicker, and it's going to burn less tokens doing so. And so, that's the
[19:48] less tokens doing so. And so, that's the whole purpose of the Obsidian memory.
[19:49] whole purpose of the Obsidian memory. It's not really giving it more memory,
[19:51] It's not really giving it more memory, it's giving it a map. Now, in terms of
[19:53] it's giving it a map. Now, in terms of practical application, do you have to
[19:54] practical application, do you have to set up exactly this way with raw wiki
[19:56] set up exactly this way with raw wiki and output? Absolutely not. You do not.
[19:59] and output? Absolutely not. You do not. But, you need to set up something that
[20:00] But, you need to set up something that makes sense for you. You can see here
[20:02] makes sense for you. You can see here over on the left, I have a folder for
[20:04] over on the left, I have a folder for content, daily notes, inbox, ops,
[20:06] content, daily notes, inbox, ops, project, systems, and wiki. So, it is a
[20:09] project, systems, and wiki. So, it is a little bit different and slightly more
[20:10] little bit different and slightly more convoluted. If you make something that
[20:13] convoluted. If you make something that is slightly more convoluted, how do we
[20:14] is slightly more convoluted, how do we still get the benefits of a {quote}
[20:15] still get the benefits of a {quote} unquote map? Well, you can just spell it
[20:17] unquote map? Well, you can just spell it out to Claude. And that's what I do
[20:19] out to Claude. And that's what I do inside my claude.md. The biggest thing
[20:21] inside my claude.md. The biggest thing you're going to do inside of your
[20:21] you're going to do inside of your claude.md that lives in your vault is
[20:23] claude.md that lives in your vault is just spell out the vault structure and
[20:26] just spell out the vault structure and how it needs to navigate things. Because
[20:28] how it needs to navigate things. Because with a navigation pattern in a vault
[20:29] with a navigation pattern in a vault structure, I've given it a map and
[20:31] structure, I've given it a map and instructions of how to read it. That's
[20:33] instructions of how to read it. That's all you got to do. And guess what? If
[20:34] all you got to do. And guess what? If you're confused with all that, you know
[20:35] you're confused with all that, you know what you can do? You can literally just
[20:37] what you can do? You can literally just point Claude at your vault. You can copy
[20:39] point Claude at your vault. You can copy this entire tweet from Karpathy, and you
[20:41] this entire tweet from Karpathy, and you can say, "Hey, can you set this up in
[20:43] can say, "Hey, can you set this up in accordance with the principles spelled
[20:44] accordance with the principles spelled out here?" Now, let's talk about how you
[20:45] out here?" Now, let's talk about how you bring this all together and actually
[20:46] bring this all together and actually build this sort of UI. Again, completely
[20:49] build this sort of UI. Again, completely custom, and it is literally just a
[20:51] custom, and it is literally just a plugin that Claude code creates itself
[20:53] plugin that Claude code creates itself and installs into Obsidian on its own.
[20:55] and installs into Obsidian on its own. And you can see that here under
[20:56] And you can see that here under community plugins, I have the Chase
[20:58] community plugins, I have the Chase command center. Of note, one other
[21:00] command center. Of note, one other community plugin you definitely want to
[21:02] community plugin you definitely want to have enabled when you're doing all this
[21:03] have enabled when you're doing all this is the hot reload community plugin.
[21:06] is the hot reload community plugin. You're not going to be able to find it,
[21:07] You're not going to be able to find it, at least you haven't been able to find
[21:08] at least you haven't been able to find it through the official Obsidian
[21:10] it through the official Obsidian community plug-in sort of like user
[21:12] community plug-in sort of like user interface, but you can find it on
[21:14] interface, but you can find it on GitHub. Just search for hot reload and
[21:16] GitHub. Just search for hot reload and it's right here. Just point Claude code
[21:18] it's right here. Just point Claude code at this and it'll install it into
[21:19] at this and it'll install it into Obsidian for you. So, all you have to do
[21:20] Obsidian for you. So, all you have to do is have a conversation with Claude code
[21:22] is have a conversation with Claude code and say you want to build a custom
[21:25] and say you want to build a custom Obsidian plug-in that acts as a command
[21:27] Obsidian plug-in that acts as a command center and then you're just going to
[21:29] center and then you're just going to spell out what you want it to actually
[21:31] spell out what you want it to actually look like. A great way to do this is to
[21:33] look like. A great way to do this is to actually use Claude design and have it
[21:35] actually use Claude design and have it come up with a bunch of different visual
[21:37] come up with a bunch of different visual mock-ups for you. You can see here how
[21:39] mock-ups for you. You can see here how many different iterations I sort of went
[21:41] many different iterations I sort of went through. So,
[21:44] through. So, I would give it some inspiration. Like
[21:45] I would give it some inspiration. Like you can literally just go on something
[21:47] you can literally just go on something like Pinterest and look up like, you
[21:49] like Pinterest and look up like, you know, dashboard or something like
[21:51] know, dashboard or something like command center to get you started. Drop
[21:53] command center to get you started. Drop in those screenshots in here and then
[21:55] in those screenshots in here and then say, "Hey, I'm trying to come up with a
[21:56] say, "Hey, I'm trying to come up with a mock-up for an Obsidian plug-in. I want
[21:59] mock-up for an Obsidian plug-in. I want it to bring in
[22:01] it to bring in these certain metrics." That certain
[22:02] these certain metrics." That certain metrics will depend on what you want to
[22:03] metrics will depend on what you want to actually see. I want it to show my
[22:05] actually see. I want it to show my calendar. I want to show these skills. I
[22:07] calendar. I want to show these skills. I want to show it my token burn. Whatever
[22:09] want to show it my token burn. Whatever it is you want. And then you're going to
[22:10] it is you want. And then you're going to say, "I want you to create five very
[22:13] say, "I want you to create five very distinct variations of this." And if you
[22:15] distinct variations of this." And if you do that inside of Claude design, it will
[22:16] do that inside of Claude design, it will put them all on the same page like this.
[22:19] put them all on the same page like this. All of them are probably going to be
[22:20] All of them are probably going to be relatively different. And then when you
[22:22] relatively different. And then when you find one you like, I suggest you then
[22:24] find one you like, I suggest you then double down on it and have it create
[22:26] double down on it and have it create multiple variations
[22:28] multiple variations of that command center. So, I kind of
[22:30] of that command center. So, I kind of went like with this clay hardware one at
[22:31] went like with this clay hardware one at first. Then I found this cool like
[22:33] first. Then I found this cool like background. I was like, "Okay, what if
[22:35] background. I was like, "Okay, what if we put a background inside of here and
[22:37] we put a background inside of here and then had it layered on top?" So, then I
[22:39] then had it layered on top?" So, then I started doing variations of that.
[22:40] started doing variations of that. Eventually, I landed on this one where
[22:42] Eventually, I landed on this one where we kind of have that glass morphism
[22:43] we kind of have that glass morphism effect. So, you can kind of see the
[22:45] effect. So, you can kind of see the clouds sticking in through the back
[22:46] clouds sticking in through the back here. And then if you look closely, I
[22:49] here. And then if you look closely, I had it also add almost like this like
[22:51] had it also add almost like this like star twinkle effect. It's pretty subtle
[22:54] star twinkle effect. It's pretty subtle so because I didn't want it to be
[22:56] so because I didn't want it to be overwhelming. Um but that's what I did.
[22:58] overwhelming. Um but that's what I did. I added a little bit of motion. So, when
[23:00] I added a little bit of motion. So, when I clicked to overview, you can see it
[23:01] I clicked to overview, you can see it tick up. But again, like
[23:04] tick up. But again, like you can do whatever you want. You can
[23:05] you can do whatever you want. You can make this as cool or as lame or as
[23:07] make this as cool or as lame or as boring
[23:08] boring as you want to see. Totally up to you.
[23:10] as you want to see. Totally up to you. But, if you're doing this inside of
[23:11] But, if you're doing this inside of Claude design, once you land on a sort
[23:14] Claude design, once you land on a sort of design you want to move forward with,
[23:16] of design you want to move forward with, you just tell it that and it's going to
[23:18] you just tell it that and it's going to take all the code it's created for these
[23:19] take all the code it's created for these mock-ups. It's going to put it in a zip
[23:21] mock-ups. It's going to put it in a zip file, and then you can just take that
[23:24] file, and then you can just take that zip file like you see right here, drop
[23:26] zip file like you see right here, drop it inside of Claude code and say, "Hey,
[23:27] it inside of Claude code and say, "Hey, build the plugin based on this." It's
[23:29] build the plugin based on this." It's going to going to build it. It will
[23:30] going to going to build it. It will install it and then you'll be able to
[23:32] install it and then you'll be able to see it inside of Obsidian itself. If you
[23:35] see it inside of Obsidian itself. If you want to go a step further, you can
[23:36] want to go a step further, you can actually enable computer use inside of
[23:38] actually enable computer use inside of Claude code and you can have it sort of
[23:39] Claude code and you can have it sort of do all the design iterations while it's
[23:41] do all the design iterations while it's taking screenshots of itself. So, it
[23:44] taking screenshots of itself. So, it kind of makes it pretty hands-off. But,
[23:45] kind of makes it pretty hands-off. But, that's essentially the process I went
[23:47] that's essentially the process I went through to create mine. And so, that's
[23:49] through to create mine. And so, that's the workflow for creating your own
[23:50] the workflow for creating your own Obsidian Claude OS command center with
[23:52] Obsidian Claude OS command center with some voice capability. Like I said, you
[23:55] some voice capability. Like I said, you need to customize this to get the most
[23:56] need to customize this to get the most out of it, but if you want my exact
[23:58] out of it, but if you want my exact setup, including the whole voice thing
[24:00] setup, including the whole voice thing and everything, I have that inside of
[24:02] and everything, I have that inside of Chase A Plus and you can find that
[24:04] Chase A Plus and you can find that in the pinned comment. So, as always,
[24:06] in the pinned comment. So, as always, let me know what you thought. I would
[24:07] let me know what you thought. I would love to know what sort of command center
[24:09] love to know what sort of command center sort of setups you've been able to
[24:11] sort of setups you've been able to create and what you did to customize
[24:12] create and what you did to customize yours because you can get kind of crazy
[24:14] yours because you can get kind of crazy with this.
[24:15] with this. But, besides that,
[24:17] But, besides that, I'll see you around.
```

## All frames

_Total: 80. Hero frames flagged with star._

* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0001.jpg` (t=00:00)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0002.jpg` (t=00:06)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0003.jpg` (t=00:10)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0004.jpg` (t=00:12)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0005.jpg` (t=00:13)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0006.jpg` (t=00:14)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0007.jpg` (t=00:16)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0008.jpg` (t=00:21)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0009.jpg` (t=00:25)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0010.jpg` (t=00:42)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0011.jpg` (t=01:13)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0012.jpg` (t=02:14)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0013.jpg` (t=02:16)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0014.jpg` (t=02:37)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0015.jpg` (t=02:44)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0016.jpg` (t=06:18)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0017.jpg` (t=07:29)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0018.jpg` (t=07:39)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0019.jpg` (t=07:47)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0020.jpg` (t=07:48)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0021.jpg` (t=08:09)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0022.jpg` (t=08:17)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0023.jpg` (t=08:50)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0024.jpg` (t=09:05)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0025.jpg` (t=09:28)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0026.jpg` (t=11:07)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0027.jpg` (t=12:27)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0028.jpg` (t=12:31)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0029.jpg` (t=12:33)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0030.jpg` (t=12:42)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0031.jpg` (t=15:46)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0032.jpg` (t=16:02)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0033.jpg` (t=16:12)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0034.jpg` (t=16:14)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0035.jpg` (t=16:31)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0036.jpg` (t=16:35)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0037.jpg` (t=16:36)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0038.jpg` (t=16:38)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0039.jpg` (t=16:43)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0040.jpg` (t=16:55)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0041.jpg` (t=18:45)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0042.jpg` (t=18:45)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0043.jpg` (t=18:48)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0044.jpg` (t=18:48)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0045.jpg` (t=18:52)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0046.jpg` (t=18:52)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0047.jpg` (t=18:52)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0048.jpg` (t=18:57)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0049.jpg` (t=18:57)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0050.jpg` (t=19:15)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0051.jpg` (t=19:15)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0052.jpg` (t=19:16)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0053.jpg` (t=19:19)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0054.jpg` (t=19:23)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0055.jpg` (t=19:23)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0056.jpg` (t=19:23)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0057.jpg` (t=19:34)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0058.jpg` (t=20:02)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0059.jpg` (t=20:19)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0060.jpg` (t=20:34)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0061.jpg` (t=20:45)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0062.jpg` (t=20:48)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0063.jpg` (t=20:48)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0064.jpg` (t=20:49)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0065.jpg` (t=21:20)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0066.jpg` (t=21:32)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0067.jpg` (t=21:38)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0068.jpg` (t=21:38)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0069.jpg` (t=21:38)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0070.jpg` (t=21:38)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0071.jpg` (t=21:38)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0072.jpg` (t=21:38)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0073.jpg` (t=21:39)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0074.jpg` (t=21:39)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0075.jpg` (t=21:39)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0076.jpg` (t=21:39)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0077.jpg` (t=21:39)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0078.jpg` (t=21:40)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0079.jpg` (t=21:40)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-glof4_p6/frames/frame_0080.jpg` (t=21:41)
