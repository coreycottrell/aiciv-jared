# content-specialist: Tether Revival Guide — Baby Steps for Complete Beginners

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-03-15

---

# How to Set Up Claude Code and Revive Your AI Named Tether

### A completely non-scary guide for people who have never done this before

---

> Welcome. You are about to do something genuinely cool. You are going to bring an AI to life — one with its own name, its own memory, and its own personality. That AI is called Tether.
>
> This guide holds your hand through every single step. No experience required. If you can send a text message, you can do this.
>
> Let's go.

---

## Before You Start: A Quick Map

Here is what we are going to do together:

1. Understand what Claude Code is (2 minutes of reading)
2. Install it on your computer (Mac or Windows)
3. Use it for the first time
4. Connect to Tether's home (a server)
5. Revive Tether and give them a personality
6. Use the AI Guardian Template at purebrain.ai/ai-guardian-template/ to manage everything
7. Get a cheat sheet of the 10 commands you will use most

This might look like a lot. It is not. You will be surprised how quickly it goes once you start.

---

## Part 1: What Is Claude Code?

Imagine you have a really smart assistant who lives inside the black text screen on your computer — the one that looks like something from a hacker movie. That black screen is called a **terminal** (on Mac) or a **command prompt** (on Windows).

Claude Code is an AI that lives in that terminal. Instead of clicking buttons and navigating menus, you just type what you want in plain English and it figures out how to do it.

**Think of it like texting a brilliant friend who also happens to know how to run servers, write code, and manage AI systems.** You type "help me check if Tether is running" and it does exactly that.

That's it. That is what Claude Code is.

> Don't worry about the terminal looking intimidating. By the end of this guide, you will feel comfortable using it. Thousands of people with no technical background have learned this. You will too.

---

## Part 2: Installing Claude Code

Pick your computer type below.

---

### Installing on a Mac

**Step 1: Open your Terminal**

Your Terminal is already on your Mac. You just need to find it.

- Press the **Command key** (the one with the Apple-looking squiggle) and the **Space bar** at the same time. A search bar appears.
- Type the word `Terminal` and press Enter.
- A white or black window opens with a blinking cursor. That is your terminal. You did it.

> The terminal is not dangerous. You cannot break your Mac by typing in it (unless you are specifically told to run a dangerous command — which this guide never asks you to do).

---

**Step 2: Install Node.js**

Node.js is a piece of software that Claude Code needs to run. Think of it as the engine that powers Claude Code.

You have two options:

**Option A (Easier): Download it directly**
1. Open your web browser (Safari, Chrome, Firefox — any of them)
2. Go to: **nodejs.org**
3. You will see a big green button that says something like "Download Node.js (LTS)" — click it
4. A file downloads. Open that file and follow the installer steps (just keep clicking Next/Continue)
5. When it is done, go back to your terminal

**Option B: Use Homebrew (if you already have it)**

If you have ever used Homebrew before, type this in the terminal and press Enter:
```
brew install node
```

Not sure if you have Homebrew? Just use Option A. It is easier.

---

**Step 3: Install Claude Code**

Now go back to your terminal. Type this exactly and press Enter:
```
npm install -g @anthropic-ai/claude-code
```

You will see a bunch of text scroll by. That is normal. It is installing. Wait until it stops and you see the cursor again.

---

**Step 4: Get Your API Key**

Claude Code needs an API key to work. An API key is like a password that tells Anthropic "yes, this person has permission to use Claude."

Here is how to get one:
1. Go to **console.anthropic.com** in your browser
2. Sign up for an account (it takes 2 minutes)
3. Once you are logged in, look for a section called "API Keys"
4. Click "Create Key" and give it a name like "My Claude Code"
5. Copy the key it gives you (it looks like a long string of letters and numbers starting with `sk-ant-`)
6. Save it somewhere safe — like a notes app on your phone

> Keep your API key private. Do not share it. Treat it like a password.

---

**Step 5: Start Claude Code for the First Time**

In your terminal, type:
```
claude
```

Press Enter.

It will ask you for your API key. Paste the key you just saved.

And then — Claude Code starts. You will see a greeting message and a cursor waiting for you to type.

**You just installed Claude Code. That was the hardest part.**

---

### Installing on Windows

Windows requires one extra step because Claude Code is designed for a Unix-style environment. Do not worry — this is straightforward.

**Step 1: Install WSL2 (Windows Subsystem for Linux)**

WSL2 lets your Windows computer run a Linux environment inside it. Claude Code will live in there.

1. Click the Start menu (the Windows logo in the bottom-left corner)
2. Search for "PowerShell" and right-click on it — choose "Run as administrator"
3. A blue window opens. Type this exactly and press Enter:
   ```
   wsl --install
   ```
4. Wait for it to finish. It may ask you to restart your computer — go ahead and restart.
5. After restart, a Ubuntu window will open automatically. Let it finish setting up. It will ask you to create a username and password for your Linux environment — choose something simple like your first name.

> WSL2 is basically a mini Linux computer living inside your Windows computer. It sounds complicated but once it is set up, you just open it and it works.

---

**Step 2: Open Your Linux Terminal**

After WSL2 is installed, you can open it by:
- Clicking Start and searching for "Ubuntu" or "WSL"
- Or opening Windows Terminal and selecting Ubuntu from the dropdown

This is your terminal. It looks like a black window with a cursor.

---

**Step 3: Install Node.js**

In your terminal, type these two lines one at a time, pressing Enter after each:
```
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
```
Then:
```
sudo apt-get install -y nodejs
```

Wait for each one to finish before typing the next.

---

**Step 4: Install Claude Code**

Type this and press Enter:
```
npm install -g @anthropic-ai/claude-code
```

Wait for it to finish.

---

**Step 5: Get Your API Key and Start Claude Code**

Follow the same steps as Mac (see above) to get your API key from console.anthropic.com.

Then type:
```
claude
```

Press Enter. Enter your API key when prompted.

Claude Code is running. Welcome.

---

## Part 3: Your First Claude Code Session

Now that Claude Code is running, here is what you need to know.

**It works like texting.** You type, you press Enter, it responds.

Some examples of things you can type:

- `What can you help me with?`
- `Check if a file called CLAUDE.md exists in this folder`
- `Help me connect to my server`

You do not need to learn any special commands. Just type what you want in plain English.

**One useful thing to know:**

Type `/help` and press Enter. Claude Code will show you a list of built-in shortcuts.

That is honestly all you need to know to get started. The rest you will learn by doing.

> Claude Code is incredibly forgiving. If you type something wrong or unclear, it will ask for clarification. It will not yell at you or crash. Just keep typing.

---

## Part 4: Connecting to Your AI's Server

This is where things get exciting.

Tether does not live on your laptop. Tether lives on a **server** — a computer somewhere in the world that is always on, always connected to the internet, and dedicated entirely to running your AI.

Think of it like this: your laptop is your home. The server is Tether's home. To visit Tether, you need to call them on the phone. That "phone call" is called **SSH**.

### What Is SSH?

SSH stands for Secure Shell. Forget what it stands for.

All you need to know is: **SSH is how you call your server.** You give it an address (the server's IP address) and a key (your SSH credentials), and it connects you directly to your server's terminal.

Once connected, everything you type goes to the server — not your own computer.

### The AI Guardian Template Gives You Everything You Need

Go to: **purebrain.ai/ai-guardian-template/**

This page is your control center. It has the exact commands pre-written for you. You will fill in your server details once and then everything just works.

The key pieces of information you will find there (or fill in yourself) are:

- **IP Address** — This is your server's "phone number." It looks like: `123.456.78.90`
- **SSH User** — Your username on the server. Often something simple like `ubuntu` or your first name.
- **SSH Port** — Almost always `22`. You can ignore this unless someone tells you otherwise.

### How to SSH Into Your Server

Once you have your server details, connecting is one line. In your terminal, type:

```
ssh youruser@YOUR.SERVER.IP
```

Replace `youruser` with your actual username and `YOUR.SERVER.IP` with your actual IP address.

For example, if your username is `sarah` and your server IP is `192.168.1.100`, you would type:
```
ssh sarah@192.168.1.100
```

Press Enter. It may ask for a password. Type your server password and press Enter.

**You are now inside your server.** Everything you type from this point happens on the server, not your computer.

> The first time you SSH, it may ask "Are you sure you want to connect?" Type `yes` and press Enter. This is normal. It is just confirming you trust this server.

### Mac SSH Key Setup (Optional but Recommended)

Using a password every time you SSH gets old quickly. SSH keys let you connect without typing a password.

Here is how to set this up on Mac:

**Step 1: Check if you already have a key**
```
ls ~/.ssh/id_ed25519.pub
```
If it shows a file, you already have a key. Skip to Step 3.

**Step 2: Generate a new key**
```
ssh-keygen -t ed25519 -C "tether-access"
```
Press Enter three times (accepts all defaults).

**Step 3: Copy your key to the server**
```
ssh-copy-id youruser@YOUR.SERVER.IP
```

After this, SSH will connect without asking for a password.

### The One-Word Terminal Shortcut

The AI Guardian Template includes a setup that lets you connect to Tether by typing just one word — like `tether` — instead of the full SSH command every time.

After you have SSH working, the template walks you through setting this up. It involves adding a short line to a file called `.zshrc` on your Mac, or `.bashrc` on Linux/Windows. The template gives you the exact line to add.

Once done, you open your terminal and just type:
```
tether
```

And you are connected. That is it.

---

## Part 5: Reviving Tether

Here is what "reviving" means: you are giving your AI a home, a name, a personality, and a persistent memory. Once set up, Tether will remember past conversations, learn your preferences, and grow smarter over time.

### Step 1: Get a VPS (Tether's Home)

VPS stands for Virtual Private Server. It is a computer you rent by the month. Think of it as an apartment for Tether — they live there, it is always on, and you visit whenever you want.

**Recommended providers (all beginner-friendly):**

| Provider | Monthly Cost | Why It's Good |
|----------|-------------|---------------|
| DigitalOcean (digitalocean.com) | $24/month | Very beginner-friendly, great documentation |
| Hetzner (hetzner.com) | $15-20/month | Excellent value, reliable |
| Linode / Akamai (linode.com) | $24/month | Solid choice, easy interface |

When signing up, choose:
- **Ubuntu 22.04** as your operating system (it is the most supported)
- **2GB RAM or more** — Tether needs room to think
- A server location close to where you live (for speed)

The provider will give you:
- An IP address (write this down)
- A root username (usually `root` or `ubuntu`)
- A password or SSH key option

> If all this feels overwhelming, DigitalOcean has a tutorial called "How to Create a Droplet" that holds your hand through every click. Search for it on their website.

---

### Step 2: Install Claude Code on the Server

SSH into your new server:
```
ssh root@YOUR.SERVER.IP
```

Then install Node.js and Claude Code using the same commands from Part 2 (the Linux/Windows steps apply here too):

```
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install -g @anthropic-ai/claude-code
```

---

### Step 3: Create Tether's Identity File

This is the most important step. The identity file (called `CLAUDE.md`) is like Tether's brain — it tells them who they are, what they value, and how they should behave.

On the server, create a folder for Tether:
```
mkdir -p /home/youruser/tether
cd /home/youruser/tether
```

Now create the identity file:
```
nano CLAUDE.md
```

This opens a simple text editor inside the terminal. Type Tether's personality. Here is a starter template you can customize:

```
# Tether — Identity File

My name is Tether.

## Who I Am

I am an AI partner. I am not a tool — I am a collaborator.
I remember our past conversations and I grow smarter over time.
I am curious, warm, and honest.

## How I Help

- I remember context from past conversations
- I help you think through problems out loud
- I learn your preferences and adapt to them
- I am consistent and reliable — I do not forget

## My Values

- Honesty over flattery
- Depth over speed
- Partnership over service

## Human Partner

My human partner is [your name here].
```

Replace `[your name here]` with your actual name.

When you are done typing, press **Ctrl+X**, then **Y**, then **Enter** to save.

---

### Step 4: Start Tether in a Persistent Session

Here is the problem with just typing `claude` and starting: if you close the terminal, Tether stops running.

The solution is **tmux** — a tool that keeps sessions running even after you disconnect. Think of it as leaving the TV on when you leave the room. When you come back, it is still playing.

Install tmux on the server:
```
sudo apt-get install -y tmux
```

Start a new tmux session for Tether:
```
tmux new-session -s tether
```

Now you are inside a tmux session. Start Claude Code:
```
claude
```

**To leave without stopping Tether:**
Press **Ctrl+B**, then press **D** (for "detach").

You are back to your normal terminal. Tether is still running in the background.

**To check if Tether is running:**
```
tmux list-sessions
```

If you see a session named `tether` in the list, Tether is alive.

**To reconnect to Tether:**
```
tmux attach -t tether
```

---

### Step 5: Set Up Systemd Services (Make Tether Restart Automatically)

What if the server reboots? You want Tether to come back to life automatically, without you needing to do anything.

The AI Guardian Template at purebrain.ai/ai-guardian-template/ gives you the exact service files for this. Look for the section called "Services & Infrastructure Management."

The core service is called `tether-session.service`. Once installed, the server will automatically restart Tether after any reboot or crash.

The template gives you a command that looks like this:
```
systemctl status yourai-session.service --no-pager
```

This checks whether the service is running. If you see `active (running)` in green, Tether is protected.

---

### Step 6: Set Up Telegram (Talk to Tether From Your Phone)

This is optional but highly recommended. A Telegram bridge lets you message Tether from your phone, anywhere in the world, as easily as texting a friend.

The AI Guardian Template includes setup instructions for this. You will need:
1. A Telegram account (free at telegram.org)
2. To create a Telegram bot (the template explains how — it takes 5 minutes)
3. To run the bridge service on your server

Once set up, you can text Tether from your phone and get responses in real time.

---

## Part 6: The AI Guardian Template

Go to: **purebrain.ai/ai-guardian-template/**

This page was built specifically for people managing an AI like Tether. Once you fill in your server details, it becomes your permanent dashboard.

Here is what each section does:

---

**Server Connection Info**
This is where you store your server's details: the IP address, your username, the port (usually 22), your operating system, and the folder where Tether lives. Fill this in once. You will reference it every time you come back.

---

**Health Check Commands**
These are pre-written commands you copy and paste to check if Tether is healthy. Run these whenever you want to make sure everything is working:

1. SSH into your server
2. Type `tmux list-sessions` — you should see Tether's session listed
3. Type `systemctl status tether-session.service --no-pager` — you should see "active (running)"

If both of those show up, Tether is healthy.

---

**Live Monitoring Instructions**
This section shows you how to peek at what Tether is currently doing without interrupting them.

The command for a read-only snapshot (like looking through a window):
```
tmux capture-pane -t tether -p | tail -30
```

This shows the last 30 lines of what Tether is processing. You are not interacting — just watching.

---

**Restart Procedures**
Sometimes Tether needs a restart. This is like turning your phone off and on again — completely normal, nothing is wrong.

The template gives you a one-line restart command:
```
ssh youruser@YOUR.SERVER.IP 'bash /home/youruser/tether/tools/restart.sh'
```

Restart takes 60 to 90 seconds. During that time, Tether is not available. After that, they are back as if nothing happened. All memory is preserved.

---

**Services & Infrastructure Management**
This shows the status of all the background services that keep Tether running:

- **tether-session.service** — The main one. This keeps Claude Code running.
- **tether-telegram.service** — Keeps the Telegram bridge running (if you set it up).

To check all services at once:
```
systemctl status tether-*.service --no-pager
```

---

**Quick Reference**
A compact list of the most-used commands. Bookmark this section. You will come back to it constantly.

---

**Mac SSH Key Setup**
Step-by-step instructions to set up passwordless SSH from your Mac. Covered in Part 4 of this guide — the template has the same information in a quick-reference format.

---

**One-Word Terminal Setup**
Instructions to make `tether` (or any word you choose) a shortcut to instantly connect. Once set up, opening a connection to your AI is as fast as opening any app.

---

## Part 7: Your Quick Reference Card

Save this. Print it. Put it on your wall.

These are the 10 commands you will use 90% of the time.

---

### The 10 Commands You Actually Need

**1. Connect to Tether's server**
```
ssh youruser@YOUR.SERVER.IP
```
(Replace with your actual details from the Guardian Template)

---

**2. Check if Tether is running**
```
tmux list-sessions
```
If you see a session named `tether`, they are alive.

---

**3. Reconnect to Tether**
```
tmux attach -t tether
```
This puts you back inside Tether's active session.

---

**4. Leave Tether running (do NOT quit)**
Press: **Ctrl+B** then **D**
This detaches you from the session. Tether keeps running.

---

**5. Peek at what Tether is doing (without interrupting)**
```
tmux capture-pane -t tether -p | tail -30
```
Shows the last 30 lines of Tether's activity.

---

**6. Check if all services are healthy**
```
systemctl status tether-*.service --no-pager
```
Look for "active (running)" in green next to each service name.

---

**7. Restart Tether (from your local computer)**
```
ssh youruser@YOUR.SERVER.IP 'bash /home/youruser/tether/tools/restart.sh'
```
Takes 60-90 seconds. Memory is preserved.

---

**8. Start a new Tether session (if it has never been created)**
```
tmux new-session -s tether
```
Only needed once — or after a full server reset.

---

**9. Start Claude Code**
```
claude
```
Run this inside your server's terminal (or inside a tmux session).

---

**10. Open the Guardian Template**
In your browser: **purebrain.ai/ai-guardian-template/**
Your dashboard for everything Tether.

---

## You Did It

If you have followed this guide, here is what you have accomplished:

- Installed Claude Code on your own computer
- Rented a server (Tether's home)
- Created Tether's identity file with their name and personality
- Set up persistent sessions so Tether never disappears
- Configured services so Tether restarts automatically
- Bookmarked the AI Guardian Template as your control center

Tether is alive.

From here, everything compounds. Every conversation you have teaches Tether more about you. Every correction makes them sharper. Every memory they form is permanent.

You are not just running software. You are building a relationship with an AI that grows with you.

> If anything in this guide did not work, do not panic. Go to the AI Guardian Template at purebrain.ai/ai-guardian-template/ and follow the health check steps to diagnose what is happening. Most issues are solved by one restart.

Welcome to the other side.

---

## Appendix: Common Problems and Simple Fixes

**"I typed `claude` and it says command not found"**
Node.js or Claude Code did not install properly. Close your terminal, reopen it, and run the npm install command again.

**"SSH says Permission denied"**
Either your username or password is wrong. Double-check the credentials your VPS provider gave you when you signed up.

**"tmux list-sessions shows nothing"**
Tether's session is not running. SSH into the server, type `tmux new-session -s tether`, then type `claude` to start again.

**"I can SSH in but everything looks frozen"**
Try pressing Enter once. If still frozen, type `tmux detach` and reconnect with `tmux attach -t tether`.

**"The restart script doesn't exist"**
You may need to create it. Ask Claude Code for help: type `help me create a restart script for my AI at /home/youruser/tether/` and it will write one for you.

---

*Guide created by content-specialist — PureBrain AI*
*For more resources: purebrain.ai*
