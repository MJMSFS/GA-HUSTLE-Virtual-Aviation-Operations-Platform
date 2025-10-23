GA HUSTLE: Virtual Aviation Operations Platform
This platform is a niche Virtual Airline (VA) management system dedicated to simulating the dynamic world of General Aviation (GA), air taxi, and small business jet operations within Microsoft Flight Simulator (MSFS). It provides a compelling break from the routine of commercial airliners by challenging pilots to "hustle" and manage highly opportunistic, point-to-point flights.

Key Features and Thematic Components:
Pilot Management Detailed pilot dashboard
pilots.db, index.html.

Job Market Focus on high-value, urgent, non-scheduled transport missions (e.g., organ transport, corporate shuttle, priority cargo) suitable for piston, turboprop, and light jet aircraft.
jobs.db, jobmarket.db, job_market.html.

Fleet Manager
Assign aircraft to jobs, track usage and availability. Needs polishing and fixing to work

Ledger System
Monitor financial transactions and mission payouts. Needs polishing and fixing to work


Technology Core Robust, lightweight web application built with Python (Flask). Uses SQLite for all application data (Pilots, Fleet, Ledger, Jobs) and Bcrypt for secure authentication.
app.py, script.js, Database setup files.
- Backend: Python (Flask)
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (Pilots, Fleet, Jobs, Ledger)
- Security: Bcrypt for password hashing


Why This Platform is Unique:

🌍 Why GA Hustle Is Different
Unlike traditional VA platforms focused on scheduled airline ops, GA Hustle celebrates:
- ✈️ Flexibility: Fly what you want, when you want.
- 🧠 Decision-making: Choose missions based on aircraft capability, urgency, and reward.
- 💼 Entrepreneurial spirit: Build your own config-driven aviation folklore.
This is for sim pilots who enjoy crafting their own aviation journey—one mission, one config tweak, one story at a time
