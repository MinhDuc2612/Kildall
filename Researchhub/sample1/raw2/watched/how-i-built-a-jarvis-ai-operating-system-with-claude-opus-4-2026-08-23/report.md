---
source: https://www.youtube.com/watch?v=E76dTNcvcWI
title: How I Built a JARVIS AI Operating System with Claude Opus 4.8
duration: 13:56
watched_at: 2026-08-23T21:51:45.753306+07:00
intent: research about it, identify the tool/project/technique being discussed, deep-research topic
hero_frames: [frame_0001.jpg, frame_0003.jpg, frame_0005.jpg, frame_0007.jpg, frame_0008.jpg]
transcript_source: captions
---

# How I Built a JARVIS AI Operating System with Claude Opus 4.8

## TL;DR

- The video is a build tutorial, not a product announcement: creator Eddie Chen demos and then walks through building "Jarvis AIOS," a personal voice-controlled "AI operating system" — a spoken assistant plus a glowing sci-fi HUD dashboard that renders live business data (subscriber counts, sales pipeline, daily brief) in sync with speech.
- The "OS" is a stitched-together stack, not a novel kernel or runtime: **LiveKit** (open-source real-time framework) provides the "room" where a Python voice agent and a Next.js/Tailwind dashboard both connect; **Deepgram** does speech-to-text; **GPT-5.1** is the reasoning "brain" with 5 tool-calls (daily brief, metrics, pipeline, intel, plan-my-day); **ElevenLabs** does text-to-speech with a cloned "Jarvis" voice.
- **Claude Code running Opus 4.8 is the code-generation tool**, not the runtime brain of the assistant — the creator pastes one long structured prompt into a `claude` CLI session and has it scaffold the entire project (agent.py, tools.py, render.py, prompts, seed data, contract.md, readme.md) in about 15 minutes.
- Coordination between the voice agent (backend) and HUD (frontend) happens via a LiveKit room data-channel convention the creator calls a "contract": tools publish JSON events under an `AIOS.render` topic with 5 fixed string-literal render types that must byte-match between the Python publisher and the Next.js consumer.
- Relevant to "agentic OS" building: this is a real (if consumer/prosumer-scale) example of the pattern — a tool-calling LLM agent wrapped in a persistent voice+visual interface layered over a business's live data — but it is a single-user demo app assembled from off-the-shelf SaaS APIs, not an operating system in the systems-software sense (no process management, scheduling, or multi-agent orchestration kernel).

## Key moments

- **[00:00-00:10] Cold-open demo** — a wake-word HUD graphic (Iron-Man-style orange ring) lights up on a monitor before any dialogue; "Hey Jarvis" / "Hey Eddie" exchange starts the demo in-medias-res (`hook_frames/frame_0001.jpg`, `frame_0010.jpg`).
- **[00:15-00:28] Voice-driven daily brief** — Eddie asks for "the brief for today"; Jarvis answers with a spoken summary (YouTube views up 76%) while the HUD renders a matching "Brief" card (`hook_frames/frame_0015.jpg`).
- **[00:31-00:47] Voice-driven metrics** — "Show me some metrics" triggers a self-drawing subscriber chart (4,030 subs, +32%) rendered live on the dashboard, synced to speech (`frames/frame_0002.jpg`).
- **[00:48-01:03] Thesis statement / title reveal** — creator states the video's actual claim: building "this Jarvis AI OS using the new Claude model Opus 4.8," i.e. voice + glowing HUD "on top of a Blue[print] Agency operating system" (`frames/frame_0003.jpg`, the 3-box "agent/web/seed" overview slide).
- **[01:03-02:30] Architecture explainer** — defines "AI OS" as an agent with full workspace/business context; names the 3 core files (agent.py = Python voice loop, web/ = Next.js HUD, seed/ = curated demo data) and the signal path: mic → speech-to-text → LLM+tools → text-to-speech → HUD render event.
- **[02:44-02:51] Stack reveal** — speech-to-text = Deepgram, LLM "brain" = GPT-5.1 (not Claude — Claude is only used to *write the code*), TTS = ElevenLabs with a cloned voice.
- **[04:55-06:43] Credential setup walkthrough** — screen-recorded signups: LiveKit (project + API key/secret/URL), Deepgram (API key, "$2,000 free credit" claimed), ElevenLabs (API key + a pre-made "Jarvis" voice clone) (`frames/frame_0004.jpg`-`frames/frame_0008.jpg`).
- **[06:59-07:20] Claude Code scaffolding step** — creator runs a `claude` CLI session ("Claude run," Opus 4.8, high reasoning effort) and pastes one long prompt asking it to build "Jarvis AI OS" in 3 parts (agent/web/seed) with all keys sourced from `.env`.
- **[09:54-10:17] The render "contract"** — explains that agent and HUD share one LiveKit room; tools publish JSON over the room's data channel under an `AIOS.render` event name with 5 literal string types (brief, metrics, pipeline, intel, actions) that must byte-match between the Python publisher and the JS consumer — documented in a `contract.md` the agent also generates.
- **[11:26-13:36] Wrap-up / lead-gen pitch** — walks through the generated file tree (agent.py, prompts, render.py, tools.py, seed data, contract.md, readme.md), plugs a free PDF setup guide, then pitches the creator's AI-automation consulting business (`frames/frame_0009.jpg`-`frame_0012.jpg`).

## Hook microscope (0-10s)

- Frames: 20 at 2 fps

Opens completely silent on a wide static shot of a home-office monitor (window blinds, city skyline visible) with the screen black except a small orange dot — then at ~2s the dot blooms into a glowing Iron-Man-style HUD ring, a visual cue that something is "waking up" before any words are spoken. Around 4-5s the creator's back/shoulder enters frame from off-camera (frame_0005) as he approaches the desk — classic in-frame reveal of "the human" after "the machine" has already been shown active. By 7-8s the ring has resolved into a labeled "Brief" HUD card floating beside the monitor (frame_0010), and the dialogue "Hey Jarvis... Hey Eddie" lands right as the visual proof (a working, speech-synced dashboard) is already on screen. This is a **demo-first hook**: no narration, no title card, no "in this video I'll show you" — the payoff (a talking AI with a live animated dashboard) is shown running before the creator explains what it is, which is the strongest hook pattern for a build-tutorial audience (prove it works, then teach it).

## Editorial profile

- Shots: 12
- Cuts/min: 0.86
- Mean shot length: 69.64s
- Median shot length: 24.32s
- Talking-head ratio: n/a (opencv not installed)

Slow-cut, screen-recording-heavy tutorial style: long unbroken shots (mean 69s) of live coding/dashboard demos and browser walkthroughs with a small talking-head webcam bubble in the corner, minimal jump-cuts, sparse on-screen text limited to slide-style overview cards and captured UI — closer to a "watch me build this" screencast than a fast-paced YouTube-Shorts edit.

## Quotable moments

- **[01:03-01:14]** "The idea is basically you have a voice assistant, which is an AI OS, which is an AI operating system... the AI agent that has the complete knowledge of your workspace, has context of your business, and it's kind of your first assistant."
- **[06:52-06:59]** "The last thing you need to do is go to use your LLM... now, all you have to do is kind of go to Claude Code" — the line that draws the sharpest boundary in the whole video: GPT-5.1 is the runtime brain, Claude Code is only the one-time builder.
- **[09:54-10:00]** "Tools publish JSON over the room data channel on something called AIOS.render" — the core technical mechanism holding the "OS" together.
- **[10:11-10:15]** "They must be byte [for] byte identical in the Python publisher" — underscores how brittle/manual the frontend-backend contract currently is.
- **[13:38-13:43]** "This is just a very quick video just to showcase what you can build nowadays with Opus 4.8, which is absolutely insane" — the creator's own framing of the video as a capability showcase, not a production system.

## Entities mentioned

- People: [[eddie-chen]] (creator, "Eddie Chen | AI Automation")
- Companies: [[anthropic]] (Claude / Claude Code / Opus 4.8), [[openai]] (GPT-5.1), [[livekit]], [[deepgram]], [[elevenlabs]], [[legacy-ai]] (creator's own consulting/agency brand shown in slide branding)
- Tools / products: Claude Code, Claude Opus 4.8, GPT-5.1, LiveKit (rooms/agents framework), Deepgram (speech-to-text API), ElevenLabs (text-to-speech / voice cloning), Next.js, Tailwind CSS, Python
- Places: none named (home office setting only)

## Concepts surfaced

- **"AI OS" / AI operating system**: the video's own working definition — a persistent, tool-calling voice agent with full context of a person's/business's workspace and data, acting as a "first assistant" for daily tasks. Not a systems-software OS (no process/resource management, no kernel) — a branding term for a voice+dashboard agent product.
- **Voice agent pipeline (STT → LLM+tools → TTS)**: the standard architecture for any voice assistant — mic → speech-to-text (Deepgram) → LLM reasoning with tool calls (GPT-5.1) → text-to-speech (ElevenLabs) — demonstrated concretely rather than invented here.
- **Shared "room" pattern (LiveKit)**: backend agent and frontend dashboard are two participants joined into the same real-time room; state changes flow as data-channel events rather than a traditional REST/poll API.
- **Render contract convention**: an informal but load-bearing agreement (documented in `contract.md`) that tool outputs map 1:1 to fixed string-literal event types (brief/metrics/pipeline/intel/actions) that must match exactly between the Python publisher and JS consumer — a fragile-by-construction integration point worth flagging for anyone replicating this.
- **LLM-as-scaffolder vs. LLM-as-runtime-brain**: Claude Code (Opus 4.8) is used purely to generate the codebase from one prompt; a separate model (GPT-5.1) is what actually reasons at runtime inside the shipped agent. This split is a recurring and easy-to-miss pattern in "built with Claude" video titles.

## Transcript

_Source: captions._

```
[00:10] Hey Jarvis. &gt;&gt; Hey Eddie. So, you want the rundown, the
[00:13] &gt;&gt; Hey Eddie. So, you want the rundown, the numbers, or help planning the day?
[00:15] numbers, or help planning the day? &gt;&gt; Jarvis, give me the brief for today.
[00:17] &gt;&gt; Jarvis, give me the brief for today. &gt;&gt; All right, here's the headline. It's a
[00:19] &gt;&gt; All right, here's the headline. It's a strong month. Top signal, your last 30
[00:21] strong month. Top signal, your last 30 days of YouTube views are up about 76%
[00:25] days of YouTube views are up about 76% and that's basically the scoreboard
[00:26] and that's basically the scoreboard saying the daily cadence is doing its
[00:28] saying the daily cadence is doing its job.
[00:28] job. &gt;&gt; Nice. Okay, how's Yeah, how's the
[00:31] &gt;&gt; Nice. Okay, how's Yeah, how's the numbers going? Show me some metrics.
[00:32] numbers going? Show me some metrics. &gt;&gt; So, on the service side of the house,
[00:35] &gt;&gt; So, on the service side of the house, Elsie, you're at about 4,030
[00:38] Elsie, you're at about 4,030 subscribers, roughly 32% over the last
[00:41] subscribers, roughly 32% over the last month. The audience is clearly saying,
[00:43] month. The audience is clearly saying, "More, please." Which is exactly what
[00:45] "More, please." Which is exactly what you want while you spin up services on
[00:47] you want while you spin up services on top.
[00:48] top. &gt;&gt; So, in this video, I'm going to show you
[00:49] &gt;&gt; So, in this video, I'm going to show you exactly how to build this Jarvis AI OS
[00:53] exactly how to build this Jarvis AI OS using the new Claude model Opus 4.8.
[00:56] using the new Claude model Opus 4.8. Let's get straight to it. So, I'm going
[00:57] Let's get straight to it. So, I'm going to show you how to build the voice and
[00:59] to show you how to build the voice and the glowing HUD on top of a Blue Agency
[01:01] the glowing HUD on top of a Blue Agency operating system. So,
[01:03] operating system. So, what the idea is basically you have a
[01:06] what the idea is basically you have a voice assistant, which is an AI OS,
[01:08] voice assistant, which is an AI OS, which is an AI operating system, which,
[01:10] which is an AI operating system, which, if you don't know already, is basically
[01:12] if you don't know already, is basically the AI agent that has the complete
[01:14] the AI agent that has the complete knowledge of your workspace, has context
[01:16] knowledge of your workspace, has context of your business, and it's kind of your
[01:18] of your business, and it's kind of your first assistant and can help you with
[01:20] first assistant and can help you with most of the tasks that you want to do
[01:22] most of the tasks that you want to do throughout the day. And the idea is that
[01:24] throughout the day. And the idea is that you can talk to it, it thinks with an
[01:25] you can talk to it, it thinks with an LLM, and it can answers out loud like a
[01:27] LLM, and it can answers out loud like a voice with a cloned voice, and it shows
[01:29] voice with a cloned voice, and it shows some of like a dashboard as you see it
[01:31] some of like a dashboard as you see it from Jarvis' screen, um that's in sync
[01:33] from Jarvis' screen, um that's in sync with the speech. So, like the
[01:34] with the speech. So, like the animations, as you can see earlier, is
[01:36] animations, as you can see earlier, is in sync with the speech. So, there are
[01:38] in sync with the speech. So, there are three files that are the most important
[01:40] three files that are the most important one. So, you have the agent, which is a
[01:43] one. So, you have the agent, which is a using Python script to build it, um
[01:45] using Python script to build it, um which is a Python voice agent. It can
[01:46] which is a Python voice agent. It can listen, think, and speak. And you have
[01:49] listen, think, and speak. And you have the HUD, which is kind of the display,
[01:50] the HUD, which is kind of the display, which is a Next.js. Again, you don't
[01:52] which is a Next.js. Again, you don't need to know what Next.js is, it's just
[01:54] need to know what Next.js is, it's just a framework for building the front end,
[01:56] a framework for building the front end, like a dashboard, but just a cool
[01:57] like a dashboard, but just a cool dashboard. And as long as the agent
[02:01] dashboard. And as long as the agent joins the same room, then starts to
[02:03] joins the same room, then starts to speak and it animates the panels, as you
[02:05] speak and it animates the panels, as you can see earlier. And the data, which is
[02:08] can see earlier. And the data, which is what it knows, kind of for now it's kind
[02:09] what it knows, kind of for now it's kind of curated for this demo, but you can
[02:11] of curated for this demo, but you can put in whatever data you want for your
[02:12] put in whatever data you want for your business, etc., right? So, essentially
[02:15] business, etc., right? So, essentially it kind kind of goes down to two paths.
[02:16] it kind kind of goes down to two paths. So, the voice kind of speaks like a
[02:18] So, the voice kind of speaks like a short human summary, and then the visual
[02:20] short human summary, and then the visual dashboard you saw earlier kind of show a
[02:22] dashboard you saw earlier kind of show a structured rendering of the event, like
[02:25] structured rendering of the event, like the daily brief kind of showing it line
[02:26] the daily brief kind of showing it line by line on the dashboard, right? And
[02:29] by line on the dashboard, right? And this is how we kind of think about
[02:30] this is how we kind of think about architecting the solution. So, first of
[02:33] architecting the solution. So, first of all, it's you who is speaking, so you
[02:35] all, it's you who is speaking, so you have a mic, right? So, you speak. And
[02:37] have a mic, right? So, you speak. And you have something that translates what
[02:39] you have something that translates what you speak audio into text, and that is
[02:42] you speak audio into text, and that is what we call a speech-to-text layer. And
[02:44] what we call a speech-to-text layer. And in this demo, we'll be using Deep
[02:45] in this demo, we'll be using Deep Ground. Then, we have AL and the agent,
[02:48] Ground. Then, we have AL and the agent, which is the brain is powered by
[02:50] which is the brain is powered by GPT-5.1.
[02:51] GPT-5.1. And it has multiple tools attached to
[02:53] And it has multiple tools attached to the GPT that it can perform certain
[02:55] the GPT that it can perform certain actions on. And after the GPT thinks,
[02:58] actions on. And after the GPT thinks, perform an action, then it output a text
[03:01] perform an action, then it output a text to go for a text-to-speech through the
[03:02] to go for a text-to-speech through the Eleven Labs, essentially, which is a
[03:04] Eleven Labs, essentially, which is a cloned Jarvis voice. And then it will
[03:07] cloned Jarvis voice. And then it will run the tools, of course. So, the tools
[03:09] run the tools, of course. So, the tools will have different outputs. So, one of
[03:10] will have different outputs. So, one of those outputs could be the animation
[03:12] those outputs could be the animation that you saw in the dashboard up just
[03:14] that you saw in the dashboard up just now. This is kind of like the overall
[03:16] now. This is kind of like the overall idea. And it has five different
[03:18] idea. And it has five different capabilities. Each one is a tool
[03:20] capabilities. Each one is a tool attached to an agent. That means that
[03:22] attached to an agent. That means that when the tool is attached to an agent,
[03:24] when the tool is attached to an agent, the agent can then call these tools at
[03:27] the agent can then call these tools at random to perform actions. One of such
[03:29] random to perform actions. One of such tools that we have is kind of get daily
[03:31] tools that we have is kind of get daily brief. So, as you heard earlier, when I
[03:34] brief. So, as you heard earlier, when I said, "Brief me on XYZ," it would create
[03:37] said, "Brief me on XYZ," it would create a brief card and the signals, right? As
[03:39] a brief card and the signals, right? As you saw earlier. And then you will see
[03:41] you saw earlier. And then you will see like, "Hey, run me some metrics." Then
[03:43] like, "Hey, run me some metrics." Then it will go show me like a subscription
[03:45] it will go show me like a subscription chart line, etc. And then it also has
[03:48] chart line, etc. And then it also has like a get pipeline, so like you can
[03:49] like a get pipeline, so like you can kind of know what's at risk right now.
[03:52] kind of know what's at risk right now. And then what was said about X is like
[03:53] And then what was said about X is like kind of searching for the messaging, and
[03:56] kind of searching for the messaging, and then how should I do my day is kind of
[03:57] then how should I do my day is kind of planning my day. So, it has five
[03:58] planning my day. So, it has five different actions you can do. Mostly
[04:00] different actions you can do. Mostly some metrics, kind of risk assessment,
[04:02] some metrics, kind of risk assessment, planning for my day, and getting a daily
[04:04] planning for my day, and getting a daily brief actions that I need to do for my
[04:06] brief actions that I need to do for my business right now, right? And something
[04:08] business right now, right? And something I've done in the back end as well is
[04:10] I've done in the back end as well is that I've actually called it AIOS demo
[04:13] that I've actually called it AIOS demo one. So, the reason why I use this demo
[04:15] one. So, the reason why I use this demo one just now just to show you so that
[04:16] one just now just to show you so that it's as a demo for you guys, but in the
[04:18] it's as a demo for you guys, but in the back end I actually have a something set
[04:21] back end I actually have a something set up so it's AIOS demo mode equals to
[04:23] up so it's AIOS demo mode equals to zero. So, it's actually live data curing
[04:25] zero. So, it's actually live data curing my actual business databases, but of
[04:27] my actual business databases, but of course I don't want to show that to you
[04:28] course I don't want to show that to you guys, right? So, I just turn it on for
[04:30] guys, right? So, I just turn it on for demo equals one. And it actually gives
[04:32] demo equals one. And it actually gives you like kind of some sort of smooth
[04:34] you like kind of some sort of smooth visuals like a self-drawing chart, which
[04:35] visuals like a self-drawing chart, which is kind of like a you don't know what's
[04:37] is kind of like a you don't know what's that yet, but it's basically a path that
[04:39] that yet, but it's basically a path that kind of animates the graph that you saw
[04:41] kind of animates the graph that you saw just now. And you also like a brief
[04:43] just now. And you also like a brief basically you will go for it letter by
[04:45] basically you will go for it letter by letter in the brief kind of line by line
[04:47] letter in the brief kind of line by line animations, right? I can do that. And
[04:49] animations, right? I can do that. And here's exactly how you're able to set
[04:51] here's exactly how you're able to set this up for your business and yourself
[04:52] this up for your business and yourself if you want to play around with it. It
[04:53] if you want to play around with it. It takes 15 minutes, even less than that.
[04:55] takes 15 minutes, even less than that. So, all you have to do is kind of go to
[04:56] So, all you have to do is kind of go to LiveKit, go to livekit.com, which is an
[04:58] LiveKit, go to livekit.com, which is an open-source framework for building AI
[04:59] open-source framework for building AI agents, and get your account. And once
[05:01] agents, and get your account. And once you're in, all you have to do is go to
[05:04] you're in, all you have to do is go to project and go to a kind of create a
[05:07] project and go to a kind of create a project. So, if you go to here, you go
[05:09] project. So, if you go to here, you go and create new projects right here. And
[05:11] and create new projects right here. And after you create a new project, you will
[05:13] after you create a new project, you will go to the project settings like this.
[05:15] go to the project settings like this. And you can see like the project ID,
[05:17] And you can see like the project ID, project URL, and zip URL, etc. Now, what
[05:20] project URL, and zip URL, etc. Now, what you actually want to do is you want to
[05:21] you actually want to do is you want to go to API keys and go ahead and go and
[05:24] go to API keys and go ahead and go and click on create key, and just name it
[05:26] click on create key, and just name it something, right? Just name it like demo
[05:29] something, right? Just name it like demo for example, and click on create key.
[05:31] for example, and click on create key. And now, you just need to copy this,
[05:33] And now, you just need to copy this, save this somewhere, which is your
[05:34] save this somewhere, which is your LiveKit URL, LiveKit API key, and
[05:37] LiveKit URL, LiveKit API key, and LiveKit API secret. It's going to be
[05:39] LiveKit API secret. It's going to be useful later on. So, just copy this and
[05:41] useful later on. So, just copy this and just close this, right? And obviously
[05:44] just close this, right? And obviously I'm just going to delete mine, I'm just
[05:45] I'm just going to delete mine, I'm just revoke mine. And now, after you're done
[05:47] revoke mine. And now, after you're done with the Live Kit, which is kind of like
[05:49] with the Live Kit, which is kind of like the framework for building kind of like
[05:51] the framework for building kind of like the If you think about like the plumbing
[05:53] the If you think about like the plumbing and set up setting up the infrastructure
[05:54] and set up setting up the infrastructure of this voice agents, and the next thing
[05:56] of this voice agents, and the next thing you need to get is Deepgram, which is a
[05:58] you need to get is Deepgram, which is a way to transcribe your voice to text.
[06:00] way to transcribe your voice to text. They give a very generous I think it's
[06:02] They give a very generous I think it's $2,000 credit or something like that.
[06:03] $2,000 credit or something like that. Very, very generous free tier. So, it's
[06:05] Very, very generous free tier. So, it's completely free. Just sign in to your
[06:07] completely free. Just sign in to your account, and yeah, just you need to
[06:09] account, and yeah, just you need to create an API key and copy this. And for
[06:12] create an API key and copy this. And for Eleven Labs, actually, if you go to
[06:14] Eleven Labs, actually, if you go to Eleven Labs and create an account, this
[06:16] Eleven Labs and create an account, this is the voice that we're going to get.
[06:17] is the voice that we're going to get. So, the voice I use actually is you go
[06:18] So, the voice I use actually is you go to voices in Eleven Labs, you just click
[06:20] to voices in Eleven Labs, you just click on Jarvis. I had it. Jarvis, right? This
[06:23] on Jarvis. I had it. Jarvis, right? This is the one. So, if you just copy this
[06:26] is the one. So, if you just copy this voice ID as well, so that you would let
[06:29] voice ID as well, so that you would let Claude code know it's kind of what
[06:30] Claude code know it's kind of what voices you want. This is the Jarvis
[06:32] voices you want. This is the Jarvis voice. And also, if you go to developers
[06:34] voice. And also, if you go to developers and you go to API keys, and then you
[06:36] and you go to API keys, and then you just create a key just now and copy this
[06:38] just create a key just now and copy this API key as well. So, you should have
[06:40] API key as well. So, you should have Eleven Labs, you have the API key, the
[06:42] Eleven Labs, you have the API key, the voice ID.
[06:43] voice ID. For Deepgram, you have the API key. For
[06:45] For Deepgram, you have the API key. For Live Kit, you have the Live Kit URL,
[06:46] Live Kit, you have the Live Kit URL, Live Kit API key, and Live Kit API
[06:49] Live Kit API key, and Live Kit API secret. So, all these things. And the
[06:50] secret. So, all these things. And the last thing you need to do is go to use
[06:52] last thing you need to do is go to use your LM. So, So, for me, I'm using
[06:54] your LM. So, So, for me, I'm using GPT, so I have an OpenAI API key. And
[06:57] GPT, so I have an OpenAI API key. And now, all you have to do is kind of go to
[06:59] now, all you have to do is kind of go to Claude code, and for me, I have a
[07:01] Claude code, and for me, I have a command which is Claude run. So, this is
[07:02] command which is Claude run. So, this is my workspace. And as you can see, I'm
[07:04] my workspace. And as you can see, I'm running Opus 4.8, which is kind of the
[07:06] running Opus 4.8, which is kind of the default settings. It's in high tier
[07:09] default settings. It's in high tier reasoning effort. And the reason why I
[07:10] reasoning effort. And the reason why I have this Claude run command is so that
[07:11] have this Claude run command is so that it has all the context for my business.
[07:14] it has all the context for my business. And what we're going to do is we're
[07:15] And what we're going to do is we're going to be creating this project. So,
[07:17] going to be creating this project. So, we're going to be creating a folder that
[07:18] we're going to be creating a folder that contains all the different scripts and
[07:20] contains all the different scripts and files for this specific agent. I've
[07:22] files for this specific agent. I've already built it, but just to let you
[07:24] already built it, but just to let you know that within this project folder, I
[07:26] know that within this project folder, I have the Jarvis iOS. And as you've seen
[07:28] have the Jarvis iOS. And as you've seen from the PowerPoint before that you have
[07:30] from the PowerPoint before that you have three files, right? We have the agents,
[07:32] three files, right? We have the agents, right? Which is the the Live Kit agent.
[07:34] right? Which is the the Live Kit agent. We have the seed, right? And the web.
[07:36] We have the seed, right? And the web. The The seed is the databases. It's kind
[07:39] The The seed is the databases. It's kind of like the demo databases that I I
[07:41] of like the demo databases that I I And the web is kind of the front end
[07:43] And the web is kind of the front end that has the HUD and the animation,
[07:45] that has the HUD and the animation, right? So, what we're going to do here
[07:47] right? So, what we're going to do here is paste in like a prompt that I already
[07:50] is paste in like a prompt that I already have. So, I will say, "Build me a Jarvis
[07:52] have. So, I will say, "Build me a Jarvis AI OS, a voice-controlled AI operating
[07:55] AI OS, a voice-controlled AI operating system with a glowing heads-up dashboard
[07:57] system with a glowing heads-up dashboard on top of my real business data. Put it
[07:59] on top of my real business data. Put it in project Jarvis AI OS in three parts.
[08:02] in project Jarvis AI OS in three parts. The agent, which is the Python, which is
[08:04] The agent, which is the Python, which is a the Live Kit agent. The web, which is
[08:07] a the Live Kit agent. The web, which is the Next.js HUD. And the seed, which is
[08:09] the Next.js HUD. And the seed, which is the demo data." Um the agent you just
[08:11] the demo data." Um the agent you just described what it is is the Live Kit
[08:12] described what it is is the Live Kit agent that voice loops to deep gram as
[08:14] agent that voice loops to deep gram as speech-to-text. The GPT-5.1 as the brain
[08:17] speech-to-text. The GPT-5.1 as the brain via a Live Kit plugin OpenAI. Eleven
[08:19] via a Live Kit plugin OpenAI. Eleven Labs text-to-speech in my clone voice,
[08:21] Labs text-to-speech in my clone voice, uh voice ID from my Eleven Labs voice
[08:23] uh voice ID from my Eleven Labs voice ID. And the VAD, which is a uh kind of
[08:26] ID. And the VAD, which is a uh kind of voice automatic detection. All keys from
[08:28] voice automatic detection. All keys from {dot}env. So, again, {dot}env is
[08:31] {dot}env. So, again, {dot}env is basically an environment file that you
[08:32] basically an environment file that you paste in all the API keys. Now, remember
[08:34] paste in all the API keys. Now, remember when I just told you to paste in all of
[08:36] when I just told you to paste in all of those secrets? This is where you will
[08:37] those secrets? This is where you will put it inside the env file in this
[08:40] put it inside the env file in this folder that this agent will create,
[08:42] folder that this agent will create, right? This is kind of like the last
[08:43] right? This is kind of like the last steps. And then you have five functions
[08:45] steps. And then you have five functions to use. Each one does two things: return
[08:47] to use. Each one does two things: return a short spoken summary and publishes a
[08:49] a short spoken summary and publishes a random event to the HUD to screen
[08:51] random event to the HUD to screen animate in sync with the voice. So, you
[08:53] animate in sync with the voice. So, you have like the get daily brief, which is
[08:54] have like the get daily brief, which is like a brief panel. Um the metrics,
[08:57] like a brief panel. Um the metrics, again, if you have a YouTube channel,
[08:58] again, if you have a YouTube channel, ask Clouder to connect to it. Like kind
[09:00] ask Clouder to connect to it. Like kind of just fetches um your subscribers,
[09:03] of just fetches um your subscribers, views, watch time, etc. You have a get
[09:05] views, watch time, etc. You have a get pipeline, which is like a deal funnel,
[09:07] pipeline, which is like a deal funnel, um at risk deals flagged. And then you
[09:08] um at risk deals flagged. And then you have a research intel, which is the
[09:10] have a research intel, which is the recent sync plus message and timeline.
[09:12] recent sync plus message and timeline. And then you have like plan my day,
[09:13] And then you have like plan my day, which is prioritize action list, right?
[09:15] which is prioritize action list, right? And then this is the system prompt
[09:16] And then this is the system prompt itself. So, these are kind of the
[09:18] itself. So, these are kind of the instructions for Clouder code to build
[09:20] instructions for Clouder code to build the AI agents and what the structure of
[09:22] the AI agents and what the structure of the AI agent looks like. But, this is
[09:24] the AI agent looks like. But, this is defines the personality of the Jarvis
[09:26] defines the personality of the Jarvis agent itself, right? So, I'll just say,
[09:28] agent itself, right? So, I'll just say, uh calm, dry, kind of witty, kind of
[09:30] uh calm, dry, kind of witty, kind of chief of staff. Concrete turn example
[09:32] chief of staff. Concrete turn example and the banned words like no,
[09:34] and the banned words like no, understood, absolutely, so it never
[09:35] understood, absolutely, so it never sounds like a bot.
[09:36] sounds like a bot. And this is the contract, let me call it
[09:38] And this is the contract, let me call it a contract. So, the agent and the heart,
[09:41] a contract. So, the agent and the heart, which is the dashboard, share one live
[09:43] which is the dashboard, share one live kit room. So, live kit has a concept
[09:45] kit room. So, live kit has a concept called room where the participants um
[09:47] called room where the participants um can join in. So, the back end, which is
[09:49] can join in. So, the back end, which is the agent, and the front end, which is
[09:51] the agent, and the front end, which is the the animation, the dashboard, joins
[09:52] the the animation, the dashboard, joins into a single room.
[09:54] into a single room. And tools publish JSON over the room
[09:56] And tools publish JSON over the room data channel on something called AI
[09:58] data channel on something called AI OS.render. And you can have five render
[10:00] OS.render. And you can have five render type strings literals. You have the
[10:02] type strings literals. You have the brief, metrics, pipeline, intel,
[10:04] brief, metrics, pipeline, intel, actions. Each one of those string
[10:07] actions. Each one of those string corresponds to the tool that you're
[10:09] corresponds to the tool that you're getting. So, these five tools correspond
[10:11] getting. So, these five tools correspond to each of these string literals, right?
[10:13] to each of these string literals, right? And they must be byte bytes identical in
[10:15] And they must be byte bytes identical in the Python publisher. Again, you don't
[10:17] the Python publisher. Again, you don't need to worry too much about this. If
[10:18] need to worry too much about this. If you don't really understand it, you can
[10:19] you don't really understand it, you can just copy paste this if you want. And
[10:21] just copy paste this if you want. And then write a contract.md documenting it.
[10:24] then write a contract.md documenting it. And then the data, um which is the data
[10:26] And then the data, um which is the data layer, so this is where the Jarvis is
[10:28] layer, so this is where the Jarvis is able to fetch the information and create
[10:30] able to fetch the information and create this amazing dashboard. So, that will be
[10:32] this amazing dashboard. So, that will be your business data. So, you will need to
[10:34] your business data. So, you will need to have a database, or maybe you have some
[10:36] have a database, or maybe you have some sort of spreadsheet of your revenue
[10:38] sort of spreadsheet of your revenue data, or CSV file, whatever you have,
[10:40] data, or CSV file, whatever you have, it's a good idea to put it inside the
[10:42] it's a good idea to put it inside the same folder, for example, inside this
[10:44] same folder, for example, inside this Jarvis AI OS folder that you already
[10:46] Jarvis AI OS folder that you already have, if you want the agent to be able
[10:49] have, if you want the agent to be able to Jarvis to be able to curate. Yeah, so
[10:51] to Jarvis to be able to curate. Yeah, so this data layer is the only thing that
[10:52] this data layer is the only thing that touches my databases. And then for me, I
[10:54] touches my databases. And then for me, I have a demo one equals to one. That's
[10:56] have a demo one equals to one. That's kind of like a demo data. And then zero
[10:58] kind of like a demo data. And then zero is the actual data inside my claw code
[11:01] is the actual data inside my claw code workspace, essentially. And then
[11:02] workspace, essentially. And then finally, we have the heart, which is
[11:04] finally, we have the heart, which is Next.js with Tailwind, which is this
[11:06] Next.js with Tailwind, which is this tech stack, which is the glowing dark
[11:07] tech stack, which is the glowing dark blue heart that joins the room, listens
[11:10] blue heart that joins the room, listens for render events, and animates the
[11:11] for render events, and animates the matching panel. The brief types in
[11:13] matching panel. The brief types in letter by letter, chart draws itself
[11:15] letter by letter, chart draws itself across the time axis, and the funnel
[11:16] across the time axis, and the funnel bars wrote
[11:18] bars wrote at risk posture. So, essentially, this
[11:20] at risk posture. So, essentially, this is teaching Jarvis like what color
[11:22] is teaching Jarvis like what color scheme you want. Actually, if you if you
[11:24] scheme you want. Actually, if you if you prefer, like this is another like hack
[11:27] prefer, like this is another like hack if you want,
[11:28] if you want, just screenshot this. Just screenshot
[11:30] just screenshot this. Just screenshot what I have here. So, I have engaged,
[11:32] what I have here. So, I have engaged, just literally screenshot this. Just
[11:34] just literally screenshot this. Just literally screenshot this and then just
[11:36] literally screenshot this and then just show this to to Claude Claude. So, this
[11:38] show this to to Claude Claude. So, this is one way of giving reference to
[11:40] is one way of giving reference to Claude, cuz he's a multi-modal model,
[11:42] Claude, cuz he's a multi-modal model, what you want to look like, right? So,
[11:44] what you want to look like, right? So, yeah. So, if you just literally put the
[11:46] yeah. So, if you just literally put the prompts in here, you should I'm not
[11:47] prompts in here, you should I'm not going to run it because I already have
[11:48] going to run it because I already have it, but then it should be able to
[11:50] it, but then it should be able to construct something similar like the
[11:51] construct something similar like the output just so you know what the output
[11:52] output just so you know what the output looks like. Again, you have the agent,
[11:54] looks like. Again, you have the agent, you have the agent.py, which is the
[11:57] you have the agent.py, which is the actual main agent profile. So, this is
[11:59] actual main agent profile. So, this is what created the agent, right? This is
[12:02] what created the agent, right? This is actually how we construct the entire
[12:04] actually how we construct the entire LifeKit AI agent.
[12:06] LifeKit AI agent. Um we have the AIOS data, so this is
[12:08] Um we have the AIOS data, so this is kind of like the fake data that I'm
[12:11] kind of like the fake data that I'm putting in for as a demo for the LifeKit
[12:14] putting in for as a demo for the LifeKit agent. And then we have the prompts,
[12:16] agent. And then we have the prompts, which is the system prompt for Jarvis,
[12:18] which is the system prompt for Jarvis, so it's quite a comprehensive. So, you
[12:20] so it's quite a comprehensive. So, you are Jarvis, the voice of Ailis' AI
[12:22] are Jarvis, the voice of Ailis' AI operating system, and how you sound, um
[12:25] operating system, and how you sound, um just play around with it, and then what
[12:26] just play around with it, and then what you can do, which is five things, right?
[12:28] you can do, which is five things, right? You have a daily brief, metrics,
[12:30] You have a daily brief, metrics, pipeline, intel, and plan, etc., right?
[12:34] pipeline, intel, and plan, etc., right? And then you have render.py.
[12:36] And then you have render.py. Again, this is basically um the file
[12:39] Again, this is basically um the file that Claude Claude should output about
[12:40] that Claude Claude should output about rendering, about the animation, right?
[12:43] rendering, about the animation, right? From the dashboard. And then you have
[12:45] From the dashboard. And then you have tools.py, which contains those five
[12:47] tools.py, which contains those five tools in which the agent.py has access
[12:50] tools in which the agent.py has access to. This is just a tools file, right?
[12:52] to. This is just a tools file, right? And then you have the seeds. Again, this
[12:53] And then you have the seeds. Again, this is just Again, just to remind you that
[12:55] is just Again, just to remind you that this is where the data is. This is just
[12:57] this is where the data is. This is just some of the fake metrics I have, so
[12:59] some of the fake metrics I have, so don't worry too much about this. And
[13:01] don't worry too much about this. And then web for the basically how the
[13:03] then web for the basically how the animation and dashboard is going to
[13:04] animation and dashboard is going to look. This is the front end, right? So,
[13:06] look. This is the front end, right? So, they usually have something like that,
[13:08] they usually have something like that, and you should have a contract.md,
[13:09] and you should have a contract.md, again, which is about the LifeKit room
[13:11] again, which is about the LifeKit room dimension to you about, and also a
[13:13] dimension to you about, and also a readme.md so that anyone who's new to
[13:15] readme.md so that anyone who's new to this project can see what you built,
[13:18] this project can see what you built, essentially. I know this is all kind of
[13:20] essentially. I know this is all kind of overwhelming, so I have actually
[13:21] overwhelming, so I have actually included a a step-by-step setup guide
[13:24] included a a step-by-step setup guide here from from that is quite that should
[13:26] here from from that is quite that should be quite explanatory. You can actually
[13:29] be quite explanatory. You can actually get that using the link in the
[13:30] get that using the link in the description and you can just get this
[13:32] description and you can just get this PDF guide and you can just plug this
[13:33] PDF guide and you can just plug this into Clock Out as well, um which it
[13:35] into Clock Out as well, um which it makes it very easy for you guys to to
[13:37] makes it very easy for you guys to to build this one. But yeah, this is just a
[13:39] build this one. But yeah, this is just a very quick video just to showcase what
[13:40] very quick video just to showcase what you can build nowadays with Opus 4.8,
[13:43] you can build nowadays with Opus 4.8, which is absolutely insane. So yeah, if
[13:45] which is absolutely insane. So yeah, if you enjoyed this kind of video, remember
[13:46] you enjoyed this kind of video, remember to like, comment, subscribe. And if
[13:47] to like, comment, subscribe. And if you're business owner and you would like
[13:48] you're business owner and you would like to work with me and my team to build AI
[13:50] to work with me and my team to build AI solutions for your business, you can use
[13:51] solutions for your business, you can use the link in the description to book a
[13:52] the link in the description to book a free discovery call with us. And yeah, I
[13:54] free discovery call with us. And yeah, I will see you in the next video.
```

## All frames

_Total: 12. Hero frames flagged with star._

* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0001.jpg` (t=00:00)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0002.jpg` (t=00:48)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0003.jpg` (t=01:01)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0004.jpg` (t=04:55)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0005.jpg` (t=06:02)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0006.jpg` (t=06:02)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0007.jpg` (t=06:13)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0008.jpg` (t=06:43)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0009.jpg` (t=11:26)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0010.jpg` (t=13:23)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0011.jpg` (t=13:28)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-382k5qj9/frames/frame_0012.jpg` (t=13:36)
