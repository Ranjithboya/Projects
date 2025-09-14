# Sales Page Quick-Answer & Lead Bot Demo

A Streamlit app that engages visitors instantly, answers FAQs with source references, nudges at the right moment, and captures leads naturally—all powered by OpenAI.

---

## Story

Visitors land on the sales page but often bounce without engaging. Quick questions about pricing, security, or integrations aren’t answered fast enough. Nudges feel random, and lead capture is clunky. We lose qualified leads because we fail to deliver instant, trusted answers and capture interest at the right moment.

---

## Problem Statement

Modern sales pages fail to convert curious visitors into leads due to a lack of real-time interaction and frictionless lead capture. We will build a lightweight, intelligent widget that:
- Engages visitors instantly with conversational prompts  
- Answers key questions clearly and contextually using OpenAI’s LLM  
- Captures leads naturally through progressive conversation, not intrusive forms  

---

## Key Requirements

1. Instant Clarity  
2. Trustable Answers (each reply cites its source)  
3. Right-Moment Nudges (triggered by linger/scroll/click)  
4. Natural Lead Capture (only after value is delivered)  
5. Message Review Mode (preview bot responses for any situation)  

---

## Features

- **Live Q&A Chat**: Ask pricing, security, integrations—and get instant, sourced answers.  
- **Knowledge Pack Upload**: Drop in a `.txt` or `.md` file to feed product details.  
- **Situation Preview**: Describe any visitor scenario and see how the bot would respond.  
- **Simple Lead Form**: Name, Email, Company Size—requested conversationally after interest.  
- **Trace / Notes Pane**: View a live session log of Q&A, nudges, and lead captures.  

---

## Tech Stack

| Layer       | Tool                       |
|-------------|----------------------------|
| UI          | Streamlit                  |
| LLM         | OpenAI Chat Completion API |
| Persistence | Streamlit Session State    |
| Upload      | Streamlit File Uploader    |

---

## Project Structure
.
├── app.py
├── config/
│   ├── faqs.json
│   ├── bot_config.json
│   ├── nudges.json
│   └── lead_fields.json
├── leads.json
├── session_trace.json
├── requirements.txt
└── README.md
