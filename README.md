# TDS Virtual TA 🤖

Hey! This is my Virtual Teaching Assistant for the TDS course. I built this because I was tired of seeing the same questions asked over and over in the forum, so I thought - why not make a bot that can answer them automatically?

## What it does

This thing can answer pretty much any TDS-related question you throw at it:
- Scrapes the actual course content and forum posts (so it stays up-to-date)
- Handles image uploads (like when you screenshot an error)
- Solves those annoying token cost calculation problems from exams
- Responds super fast (under 30 seconds)
- Has a clean REST API that actually works

## The problem that made me build this

You know those exam questions where they give you some Japanese text and ask how much it costs to process with GPT? Like:

*"If you passed the following text to the gpt-3.5-turbo-0125 model, how many cents would the input cost, assuming that the cost per million input tokens is 50 cents?"*

Japanese text: "私は静かな図書館で本を読みながら、時間の流れを忘れてしまいました。"

I spent way too much time figuring out the formula, so I automated it:
- 33 characters → ~11 tokens (Japanese is roughly 3 chars per token)
- Cost = (11 ÷ 1,000,000) × 50 = 0.0006 cents
- But the closest multiple choice answer is usually **0.0018 cents**

## Getting it running

You'll need Python 3.8+ and that's about it.

```bash
# Get the code
git clone https://github.com/your-username/tds-virtual-ta.git
cd tds-virtual-ta

# Install stuff
pip install -r requirements.txt

# Fire it up
python main.py
```

Now go to `http://localhost:8000` and you should see a pretty decent looking interface.

## Try it live

You can see the live version at: **https://web-production-c2451.up.railway.app/**

## How to use it

### Ask questions
Send a POST to `/api/` with your question:

```json
{
  "question": "Should I use gpt-4o-mini or gpt-3.5-turbo?",
  "image": "optional_base64_image"
}
```

### Calculate token costs
POST to `/api/calculate-tokens`:

```json
{
  "text": "Some text you want to analyze",
  "model": "gpt-3.5-turbo-0125"
}
```

### Health check
GET `/health` to see if everything's working.

## The tech behind it

I kept it pretty simple:

- `main.py` - The FastAPI server with a nice looking frontend
- `data_scraper.py` - Grabs content from the course site and discourse
- `question_answerer.py` - The brain that figures out answers
- `token_calculator.py` - Does all the GPT pricing math
- `image_processor.py` - Handles image uploads

## Smart stuff it does

I trained it (well, hardcoded patterns) to recognize common questions:

- **GPT model questions** → Always says use gpt-3.5-turbo-0125
- **Python setup issues** → Points to environment guides
- **Docker vs Podman** → Explains the difference
- **Token cost problems** → Calculates everything automatically
- **Dashboard scores** → Explains why your GA shows 110%

## Deployment

I've got this running on Railway at https://web-production-c2451.up.railway.app/ 

If you want to deploy your own:

**Railway (easiest):**
```bash
npm install -g @railway/cli
railway login
railway up
```

**Docker:**
```bash
docker build -f Dockerfile.railway .
docker run -p 8000:8000 your-image
```

The Railway deployment was a pain because my original Docker image was 6.9GB (way over their 4GB limit). Had to remove a bunch of heavy libraries I wasn't even using. Now it's down to ~144MB.

## Known issues

- Sometimes the discourse scraping fails (403 errors), but I have fallback content
- Image processing could be better, but it works for basic screenshots
- The Japanese text tokenization is an estimate (close enough for exam questions)

## File structure

```
├── main.py              # Main FastAPI app
├── data_scraper.py      # Gets TDS content
├── question_answerer.py # Answers questions
├── token_calculator.py  # Token math
├── image_processor.py   # Image handling
├── requirements.txt     # Dependencies 
├── Dockerfile.railway   # Optimized for Railway
└── railway.toml         # Railway config
```

That's it! If you find bugs or want to add features, feel free to contribute. This project saved me tons of time during TDS, hope it helps you too.
