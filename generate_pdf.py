from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ── Colour palette ────────────────────────────────────────────────────
C_BG      = colors.HexColor('#0a0e1a')
C_ACCENT  = colors.HexColor('#00d4ff')
C_GREEN   = colors.HexColor('#00c875')
C_ORANGE  = colors.HexColor('#ff8c00')
C_RED     = colors.HexColor('#ff3b5c')
C_TEXT    = colors.HexColor('#1a1a2e')
C_MUTED   = colors.HexColor('#4a5568')
C_SURFACE = colors.HexColor('#f0f4f8')
C_BORDER  = colors.HexColor('#cbd5e0')
C_HEADER  = colors.HexColor('#1a365d')
C_WHITE   = colors.white

W, H = A4

doc = SimpleDocTemplate(
    '/home/claude/sentinel_setup_guide.pdf',
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm,
)

styles = getSampleStyleSheet()

# Custom styles
def sty(name, **kw):
    return ParagraphStyle(name, **kw)

S = {
    'title': sty('title',
        fontSize=28, fontName='Helvetica-Bold', textColor=C_WHITE,
        alignment=TA_CENTER, spaceAfter=6),
    'subtitle': sty('subtitle',
        fontSize=13, fontName='Helvetica', textColor=colors.HexColor('#a0c4ff'),
        alignment=TA_CENTER, spaceAfter=4),
    'h1': sty('h1',
        fontSize=16, fontName='Helvetica-Bold', textColor=C_HEADER,
        spaceBefore=18, spaceAfter=8, borderPad=4),
    'h2': sty('h2',
        fontSize=12, fontName='Helvetica-Bold', textColor=C_ACCENT,
        spaceBefore=12, spaceAfter=6),
    'h3': sty('h3',
        fontSize=10, fontName='Helvetica-Bold', textColor=C_HEADER,
        spaceBefore=8, spaceAfter=4),
    'body': sty('body',
        fontSize=9.5, fontName='Helvetica', textColor=C_TEXT,
        leading=15, spaceAfter=4),
    'code': sty('code',
        fontSize=8.5, fontName='Courier', textColor=colors.HexColor('#1a202c'),
        backColor=colors.HexColor('#edf2f7'), leading=13,
        leftIndent=8, rightIndent=8, spaceBefore=2, spaceAfter=2,
        borderPad=6),
    'code_inline': sty('code_inline',
        fontSize=8.5, fontName='Courier', textColor=colors.HexColor('#2d3748'),
        backColor=colors.HexColor('#edf2f7')),
    'note': sty('note',
        fontSize=9, fontName='Helvetica-Oblique', textColor=C_MUTED,
        leftIndent=12, spaceAfter=4),
    'bullet': sty('bullet',
        fontSize=9.5, fontName='Helvetica', textColor=C_TEXT,
        leftIndent=16, firstLineIndent=-10, leading=14, spaceAfter=3),
    'step_num': sty('step_num',
        fontSize=22, fontName='Helvetica-Bold', textColor=C_ACCENT,
        alignment=TA_CENTER),
    'toc_item': sty('toc_item',
        fontSize=10, fontName='Helvetica', textColor=C_TEXT,
        leftIndent=8, spaceAfter=5, leading=16),
    'warning': sty('warning',
        fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#7b341e'),
        spaceAfter=2),
    'tip': sty('tip',
        fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a4731'),
        spaceAfter=2),
}

def hr(color=C_BORDER, thickness=0.5):
    return HRFlowable(width='100%', thickness=thickness, color=color, spaceAfter=6, spaceBefore=6)

def code_block(*lines):
    """Render lines as a styled code block table."""
    text = '\n'.join(lines)
    return Table(
        [[Paragraph(text, S['code'])]],
        colWidths=[W - 4*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#edf2f7')),
            ('BOX',        (0,0), (-1,-1), 0.5, C_BORDER),
            ('LEFTPADDING',  (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING',   (0,0), (-1,-1), 8),
            ('BOTTOMPADDING',(0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.HexColor('#edf2f7')]),
        ])
    )

def info_box(label, text, bg=colors.HexColor('#ebf8ff'), border=C_ACCENT):
    return Table(
        [[Paragraph(f'<b>{label}</b> {text}', S['body'])]],
        colWidths=[W - 4*cm],
        style=TableStyle([
            ('BACKGROUND',   (0,0), (-1,-1), bg),
            ('BOX',          (0,0), (-1,-1), 1, border),
            ('LEFTPADDING',  (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING',   (0,0), (-1,-1), 7),
            ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ])
    )

def warn_box(text):
    return info_box('⚠  Warning:', text,
                    bg=colors.HexColor('#fffbeb'), border=C_ORANGE)

def tip_box(text):
    return info_box('✅  Tip:', text,
                    bg=colors.HexColor('#f0fff4'), border=C_GREEN)

def section_header(number, title, subtitle=''):
    data = [[
        Paragraph(str(number), S['step_num']),
        [Paragraph(title, S['h1']),
         Paragraph(subtitle, S['note']) if subtitle else Spacer(0,0)]
    ]]
    return Table(data, colWidths=[1.4*cm, W - 5.4*cm],
        style=TableStyle([
            ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING',  (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING',   (0,0), (-1,-1), 0),
            ('BOTTOMPADDING',(0,0), (-1,-1), 0),
        ])
    )

def bullet(text):
    return Paragraph(f'• {text}', S['bullet'])

story = []

# ══════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════
cover_top = Table(
    [[Paragraph('🛡 PROJECT SENTINEL', S['title']),
      Paragraph('Complete Setup &amp; Installation Guide', S['subtitle']),
      Paragraph('Agentic-AI Framework for Proactive Threat Intelligence', S['subtitle']),
    ]],
    colWidths=[W - 4*cm],
    style=TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), C_BG),
        ('TOPPADDING',   (0,0), (-1,-1), 28),
        ('BOTTOMPADDING',(0,0), (-1,-1), 28),
        ('LEFTPADDING',  (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('ROUNDEDCORNERS', (0,0), (-1,-1), 8),
    ])
)
story.append(cover_top)
story.append(Spacer(1, 0.6*cm))

meta_rows = [
    ['Document Type', 'Final Year Project — Installation Guide'],
    ['Version',       '1.0.0'],
    ['Tech Stack',    'Python 3.12 · FastAPI · React 18 · Docker · SQLite/PostgreSQL'],
    ['Target OS',     'Windows 10/11 · macOS 12+ · Ubuntu 20.04+'],
    ['Prerequisite',  'Basic command-line familiarity'],
]
meta_table = Table(meta_rows, colWidths=[4*cm, W - 8*cm],
    style=TableStyle([
        ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('TEXTCOLOR',    (0,0), (0,-1), C_HEADER),
        ('TEXTCOLOR',    (1,0), (1,-1), C_TEXT),
        ('BACKGROUND',   (0,0), (-1,-1), C_SURFACE),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[C_SURFACE, colors.HexColor('#e8edf3')]),
        ('BOX',          (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',    (0,0), (-1,-1), 0.3, C_BORDER),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 10),
    ])
)
story.append(meta_table)
story.append(Spacer(1, 0.4*cm))

story.append(tip_box(
    'This guide covers EVERY step from zero to running Project Sentinel on your machine. '
    'Each section is independent — jump to any section if you already have a tool installed.'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════
story.append(Paragraph('Table of Contents', S['h1']))
story.append(hr(C_ACCENT, 1))
toc = [
    ('1', 'System Requirements'),
    ('2', 'Installing Python 3.12'),
    ('3', 'Installing Node.js 20 (LTS)'),
    ('4', 'Installing Git'),
    ('5', 'Installing Docker Desktop'),
    ('6', 'Project Setup — Backend (FastAPI)'),
    ('7', 'Project Setup — Frontend (React)'),
    ('8', 'Running the Full Stack'),
    ('9', 'Using the Dashboard — Step by Step'),
    ('10','Optional: API Keys (OpenAI + Shodan)'),
    ('11','Docker Deployment (One Command)'),
    ('12','Troubleshooting'),
    ('13','Project Architecture Reference'),
]
for num, title in toc:
    story.append(Paragraph(f'<b>{num}.</b>  {title}', S['toc_item']))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 1 — SYSTEM REQUIREMENTS
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(1, 'System Requirements'))
story.append(hr(C_ACCENT, 1))

req_data = [
    ['Component',   'Minimum',          'Recommended'],
    ['CPU',         'Intel i3 / AMD Ryzen 3', 'Intel i5/i7 · Ryzen 5/7'],
    ['RAM',         '4 GB',             '8 GB or more'],
    ['Storage',     '5 GB free space',  '20 GB SSD'],
    ['OS',          'Windows 10 / macOS 11 / Ubuntu 18.04', 'Windows 11 / macOS 13 / Ubuntu 22.04'],
    ['Internet',    'Required',         'Stable broadband (for scanning)'],
    ['Python',      '3.10+',            '3.12 (recommended)'],
    ['Node.js',     '18+',              '20 LTS'],
]
req_table = Table(req_data, colWidths=[3.5*cm, 5.5*cm, 6*cm],
    style=TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('BACKGROUND',   (0,0), (-1,0),  C_HEADER),
        ('TEXTCOLOR',    (0,0), (-1,0),  C_WHITE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [C_WHITE, C_SURFACE]),
        ('BOX',          (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',    (0,0), (-1,-1), 0.3, C_BORDER),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('ALIGN',        (0,0), (-1,-1), 'LEFT'),
    ])
)
story.append(req_table)
story.append(Spacer(1, 0.4*cm))
story.append(warn_box(
    'Do not run Sentinel against domains you do not own or have explicit written '
    'permission to test. Unauthorized scanning is illegal. Use example.com, '
    'your own domain, or a purpose-built lab target for testing.'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 2 — PYTHON
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(2, 'Installing Python 3.12',
    'Required for the FastAPI backend and all AI agents'))
story.append(hr(C_ACCENT, 1))

story.append(Paragraph('2.1  Windows', S['h2']))
story.append(bullet('Open your browser and go to: https://www.python.org/downloads/'))
story.append(bullet('Click the yellow "Download Python 3.12.x" button at the top.'))
story.append(bullet('Run the downloaded installer (.exe file).'))
story.append(Paragraph(
    '<b>CRITICAL:</b> On the first installer screen, check the box that says '
    '"<b>Add Python to PATH</b>" before clicking Install Now.', S['body']))
story.append(bullet('Click "Install Now" and wait for completion.'))
story.append(bullet('Verify installation: open Command Prompt (Win+R → type cmd → Enter) and run:'))
story.append(code_block('python --version', '# Expected output: Python 3.12.x'))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph('2.2  macOS', S['h2']))
story.append(bullet('Option A (Recommended): Install via Homebrew'))
story.append(code_block(
    '# First install Homebrew if you do not have it:',
    '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
    '',
    '# Then install Python:',
    'brew install python@3.12',
    '',
    '# Verify:',
    'python3 --version'
))
story.append(bullet('Option B: Download .pkg from https://www.python.org/downloads/ and run it.'))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph('2.3  Ubuntu / Linux', S['h2']))
story.append(code_block(
    'sudo apt update && sudo apt upgrade -y',
    'sudo apt install -y python3.12 python3.12-venv python3-pip',
    '',
    '# Verify:',
    'python3.12 --version'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 3 — NODE.JS
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(3, 'Installing Node.js 20 (LTS)',
    'Required for the React dashboard frontend'))
story.append(hr(C_ACCENT, 1))

story.append(Paragraph('3.1  Windows', S['h2']))
story.append(bullet('Go to: https://nodejs.org/en/download'))
story.append(bullet('Click the "LTS" tab and download the Windows Installer (.msi).'))
story.append(bullet('Run the installer and accept all defaults.'))
story.append(bullet('Verify in a NEW Command Prompt window:'))
story.append(code_block('node --version', 'npm --version', '# Expected: v20.x.x and 10.x.x'))

story.append(Paragraph('3.2  macOS', S['h2']))
story.append(code_block('brew install node@20', '', 'node --version', 'npm --version'))

story.append(Paragraph('3.3  Ubuntu / Linux', S['h2']))
story.append(code_block(
    'curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -',
    'sudo apt install -y nodejs',
    '',
    'node --version',
    'npm --version'
))
story.append(Spacer(1, 0.3*cm))
story.append(tip_box(
    'If you see "npm: command not found" on Linux, run: '
    'sudo apt install -y npm'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 4 — GIT
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(4, 'Installing Git', 'Version control — also used for project setup'))
story.append(hr(C_ACCENT, 1))

story.append(Paragraph('4.1  Windows', S['h2']))
story.append(bullet('Download from: https://git-scm.com/download/win'))
story.append(bullet('Run the installer. Accept all defaults. On the "Adjusting PATH" step, '
                    'select "Git from the command line and also from 3rd-party software".'))
story.append(code_block('git --version', '# Expected: git version 2.x.x'))

story.append(Paragraph('4.2  macOS', S['h2']))
story.append(code_block('xcode-select --install   # installs git automatically', '',
                         '# OR via Homebrew:', 'brew install git'))

story.append(Paragraph('4.3  Linux', S['h2']))
story.append(code_block('sudo apt install -y git', 'git --version'))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 5 — DOCKER
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(5, 'Installing Docker Desktop',
    'Optional — needed only for the one-command Docker deployment'))
story.append(hr(C_ACCENT, 1))
story.append(info_box('ℹ Note:', 'Docker is optional. The project runs perfectly without Docker. '
             'Use sections 6–8 for the standard local setup.',
             bg=colors.HexColor('#ebf8ff'), border=C_ACCENT))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph('5.1  Windows & macOS', S['h2']))
story.append(bullet('Download Docker Desktop from: https://www.docker.com/products/docker-desktop/'))
story.append(bullet('Run the installer and follow the setup wizard.'))
story.append(bullet('Start Docker Desktop from your Applications/Start menu.'))
story.append(bullet('Wait for the whale icon in the taskbar/menubar to stop animating (Docker is ready).'))
story.append(code_block('docker --version', 'docker-compose --version'))

story.append(Paragraph('5.2  Linux (Ubuntu)', S['h2']))
story.append(code_block(
    '# Install Docker Engine',
    'sudo apt update',
    'sudo apt install -y docker.io docker-compose',
    'sudo systemctl start docker',
    'sudo systemctl enable docker',
    '',
    '# Add yourself to docker group (no sudo needed)',
    'sudo usermod -aG docker $USER',
    'newgrp docker',
    '',
    '# Verify',
    'docker --version'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 6 — BACKEND SETUP
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(6, 'Project Setup — Backend (FastAPI)',
    'The Python AI agent pipeline and REST API'))
story.append(hr(C_ACCENT, 1))

story.append(Paragraph('Step 1 — Extract the Project', S['h2']))
story.append(bullet('Extract the provided ZIP file to a location of your choice.'))
story.append(bullet('Example locations:'))
story.append(code_block(
    '# Windows:   C:\\Projects\\sentinel\\',
    '# macOS:     ~/Projects/sentinel/',
    '# Linux:     ~/sentinel/'
))

story.append(Paragraph('Step 2 — Open Terminal / Command Prompt', S['h2']))
for line in [
    'Windows: Press Win+R, type cmd, press Enter. Or use Windows Terminal.',
    'macOS:   Press Cmd+Space, type Terminal, press Enter.',
    'Linux:   Press Ctrl+Alt+T or search "Terminal".',
]:
    story.append(bullet(line))

story.append(Paragraph('Step 3 — Navigate to the Backend Directory', S['h2']))
story.append(code_block(
    '# Replace the path with where you extracted the ZIP:',
    '',
    '# Windows:',
    'cd C:\\Projects\\sentinel\\backend',
    '',
    '# macOS / Linux:',
    'cd ~/Projects/sentinel/backend'
))

story.append(Paragraph('Step 4 — Create a Virtual Environment (Recommended)', S['h2']))
story.append(code_block(
    '# Windows:',
    'python -m venv venv',
    'venv\\Scripts\\activate',
    '',
    '# macOS / Linux:',
    'python3.12 -m venv venv',
    'source venv/bin/activate',
    '',
    '# You should see (venv) at the start of your prompt'
))

story.append(Paragraph('Step 5 — Install Python Dependencies', S['h2']))
story.append(code_block(
    'pip install -r requirements.txt',
    '',
    '# This installs: FastAPI, SQLAlchemy, httpx, pydantic, uvicorn, openai, etc.',
    '# Takes 1-3 minutes on first run.'
))
story.append(tip_box('If pip is slow, try: pip install -r requirements.txt -i https://pypi.org/simple/'))

story.append(Paragraph('Step 6 — Configure Environment Variables', S['h2']))
story.append(code_block(
    '# Windows:',
    'copy .env.example .env',
    '',
    '# macOS / Linux:',
    'cp .env.example .env',
    '',
    '# The default .env works out of the box with SQLite.',
    '# Optionally open .env in Notepad/VSCode to add API keys.'
))

story.append(Paragraph('Step 7 — Start the Backend Server', S['h2']))
story.append(code_block(
    '# Make sure you are in the backend/ directory with venv activated',
    '',
    'uvicorn main:app --reload --host 0.0.0.0 --port 8000',
    '',
    '# You should see:',
    '# INFO:     Application startup complete.',
    '# INFO:     Uvicorn running on http://0.0.0.0:8000'
))
story.append(Spacer(1, 0.2*cm))
story.append(tip_box(
    'Keep this terminal window open. The backend must stay running while you use the dashboard. '
    'Open a NEW terminal window for the frontend setup.'
))
story.append(Paragraph(
    'You can verify the backend is running by opening: '
    'http://localhost:8000/docs in your browser — you should see the Swagger UI API documentation.',
    S['body']
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 7 — FRONTEND SETUP
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(7, 'Project Setup — Frontend (React)',
    'The live dashboard with charts, scan results, and reports'))
story.append(hr(C_ACCENT, 1))

story.append(Paragraph('Step 1 — Open a NEW Terminal Window', S['h2']))
story.append(bullet('Do NOT close the backend terminal. Open a fresh one.'))

story.append(Paragraph('Step 2 — Navigate to the Frontend Directory', S['h2']))
story.append(code_block(
    '# Windows:',
    'cd C:\\Projects\\sentinel\\frontend',
    '',
    '# macOS / Linux:',
    'cd ~/Projects/sentinel/frontend'
))

story.append(Paragraph('Step 3 — Install Node.js Dependencies', S['h2']))
story.append(code_block(
    'npm install',
    '',
    '# This installs React, Tailwind CSS, Recharts, Vite, etc.',
    '# Takes 1-3 minutes. You will see a node_modules/ folder created.'
))
story.append(warn_box(
    'If you see "npm: command not found", Node.js is not installed or not in PATH. '
    'Go back to Section 3 and install Node.js, then open a FRESH terminal.'
))

story.append(Paragraph('Step 4 — Start the Frontend Dev Server', S['h2']))
story.append(code_block(
    'npm run dev',
    '',
    '# You should see:',
    '#   VITE v5.x.x  ready in 500ms',
    '#   -> Local:   http://localhost:5173/',
    '#   -> Network: http://192.168.x.x:5173/'
))
story.append(Spacer(1, 0.2*cm))
story.append(tip_box(
    'Open http://localhost:5173 in your browser. '
    'You should see the Project Sentinel dashboard with a dark cybersecurity theme.'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 8 — RUNNING THE FULL STACK
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(8, 'Running the Full Stack',
    'Summary: both terminals you need open simultaneously'))
story.append(hr(C_ACCENT, 1))

story.append(Paragraph(
    'You need TWO terminal windows open at all times:', S['body']))

run_data = [
    ['Terminal', 'Directory',       'Command',                        'Port'],
    ['1 (Backend)', 'sentinel/backend', 'uvicorn main:app --reload', '8000'],
    ['2 (Frontend)', 'sentinel/frontend', 'npm run dev',             '5173'],
]
run_table = Table(run_data, colWidths=[3*cm, 4.5*cm, 5.5*cm, 2*cm],
    style=TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('BACKGROUND',   (0,0), (-1,0),  C_HEADER),
        ('TEXTCOLOR',    (0,0), (-1,0),  C_WHITE),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [C_WHITE, C_SURFACE]),
        ('BOX',          (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',    (0,0), (-1,-1), 0.3, C_BORDER),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
    ])
)
story.append(run_table)
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph('Quick-Access URLs', S['h2']))
url_data = [
    ['URL',                         'Description'],
    ['http://localhost:5173',        'Sentinel Dashboard (main app)'],
    ['http://localhost:8000',        'Backend API root'],
    ['http://localhost:8000/docs',   'Swagger API documentation (interactive)'],
    ['http://localhost:8000/health', 'Health check endpoint'],
]
url_table = Table(url_data, colWidths=[6*cm, 9*cm],
    style=TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,-1), 'Courier'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('BACKGROUND',   (0,0), (-1,0),  C_HEADER),
        ('TEXTCOLOR',    (0,0), (-1,0),  C_WHITE),
        ('TEXTCOLOR',    (0,1), (0,-1),  colors.HexColor('#0070c0')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [C_WHITE, C_SURFACE]),
        ('BOX',          (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',    (0,0), (-1,-1), 0.3, C_BORDER),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
    ])
)
story.append(url_table)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 9 — USING THE DASHBOARD
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(9, 'Using the Dashboard — Step by Step'))
story.append(hr(C_ACCENT, 1))

steps = [
    ('Open the Dashboard',
     'Navigate to http://localhost:5173 in Chrome or Firefox. '
     'You will see the dark-themed Sentinel dashboard.'),
    ('Start a New Scan',
     'Click "Scans" in the left sidebar. Enter a target domain in the input box '
     '(e.g., example.com) and click "Launch Scan". The scan is immediately queued.'),
    ('Watch the Pipeline Run',
     'The scan detail page auto-refreshes every 3 seconds. You will see the status '
     'change from PENDING → RUNNING → COMPLETED. The three agents '
     '(Scout, Analyst, Oracle) run sequentially in the background.'),
    ('View Discovered Assets',
     'Click the "Assets" tab on the scan detail page. Every subdomain, IP address, '
     'open port, and service discovered by the Scout Agent appears here with risk ratings.'),
    ('Review Vulnerabilities',
     'Click the "Vulns" tab. Vulnerabilities are listed by severity (Critical → Low). '
     'Click any vulnerability to see the CVE ID, description, CVSS score, and remediation steps.'),
    ('Read the AI Report',
     'Click the "AI Report" tab. The Oracle Agent has generated a full executive summary, '
     'technical analysis, threat actor mapping, attack vectors, and a prioritized remediation plan.'),
    ('Cross-Scan Views',
     'Use the "Assets" and "Vulnerabilities" pages in the sidebar to see aggregated data '
     'across ALL your scans in one place.'),
    ('Reports Library',
     'The "Reports" page shows all generated reports side-by-side. '
     'Click any report to read it in the right-side viewer.'),
]
for i, (title, desc) in enumerate(steps, 1):
    story.append(Paragraph(f'Step {i}: {title}', S['h3']))
    story.append(Paragraph(desc, S['body']))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 10 — API KEYS
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(10, 'Optional: API Keys',
    'OpenAI and Shodan — the app works without these'))
story.append(hr(C_ACCENT, 1))

story.append(info_box('ℹ Important:',
    'Project Sentinel is fully functional WITHOUT any API keys. '
    'The built-in threat intelligence database and deterministic report generator '
    'provide complete results for demonstrations and academic use.',
    bg=colors.HexColor('#ebf8ff'), border=C_ACCENT))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('10.1  OpenAI API Key (Enhances report quality)', S['h2']))
story.append(bullet('Go to: https://platform.openai.com/api-keys'))
story.append(bullet('Create an account and generate a new API key.'))
story.append(bullet('Open backend/.env and set: OPENAI_API_KEY=sk-your-key-here'))
story.append(bullet('Restart the backend. Oracle Agent will now use GPT for polished reports.'))

story.append(Paragraph('10.2  Shodan API Key (Enhances asset discovery)', S['h2']))
story.append(bullet('Go to: https://account.shodan.io/register'))
story.append(bullet('Register for a free account (free tier = 100 queries/month).'))
story.append(bullet('Find your API key at: https://account.shodan.io'))
story.append(bullet('Open backend/.env and set: SHODAN_API_KEY=your-key-here'))
story.append(bullet('Restart the backend. Scout Agent will enrich results with Shodan data.'))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 11 — DOCKER
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(11, 'Docker Deployment',
    'Run the entire stack with one command'))
story.append(hr(C_ACCENT, 1))
story.append(Paragraph(
    'If Docker Desktop is installed (Section 5), you can run the full '
    'frontend + backend stack with a single command:', S['body']))

story.append(code_block(
    '# From the root sentinel/ directory:',
    'cd sentinel',
    '',
    '# Build and start all services:',
    'docker-compose up --build',
    '',
    '# Wait for both services to start (~2-3 minutes on first run)',
    '# Then open: http://localhost:3000'
))
story.append(Spacer(1, 0.2*cm))
story.append(code_block(
    '# To stop everything:',
    'docker-compose down',
    '',
    '# To rebuild after code changes:',
    'docker-compose up --build --force-recreate'
))
story.append(tip_box(
    'Docker is ideal for demonstrations — it guarantees identical behaviour '
    'on any machine. Show your supervisor the docker-compose up output '
    'to demonstrate DevOps/cloud deployment knowledge.'
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 12 — TROUBLESHOOTING
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(12, 'Troubleshooting'))
story.append(hr(C_ACCENT, 1))

problems = [
    ('"python" is not recognized (Windows)',
     'Python is not in PATH. Uninstall Python and reinstall, making sure to tick "Add Python to PATH" on the first installer screen.'),
    ('"pip" is not recognized',
     'Run: python -m pip install -r requirements.txt  (use "python -m pip" instead of "pip")'),
    ('"ModuleNotFoundError: No module named fastapi"',
     'The virtual environment is not activated, or requirements were not installed in it. '
     'Activate venv first (source venv/bin/activate), then re-run pip install -r requirements.txt'),
    ('Frontend shows "Failed to create scan" error',
     'The backend is not running. Go to Terminal 1, navigate to backend/, and run: uvicorn main:app --reload'),
    ('"CORS error" in browser console',
     'The backend CORS settings already allow localhost:5173 and localhost:3000. '
     'Make sure you are opening the dashboard via http://localhost:5173 (not a file:// URL).'),
    ('"npm install" fails with EACCES (macOS/Linux)',
     'Run: sudo npm install  OR fix permissions: sudo chown -R $USER ~/.npm'),
    ('Port 8000 already in use',
     'Another service is on port 8000. Run the backend on a different port: '
     'uvicorn main:app --reload --port 8001  then update vite.config.js proxy to port 8001.'),
    ('Scan stays in PENDING forever',
     'Check the backend terminal for error messages. Common cause: DNS resolution failing '
     'for the target domain. Try scanning a well-known domain like github.com or google.com.'),
    ('Docker: "port is already allocated"',
     'Stop any other services on ports 3000 or 8000 first, then re-run docker-compose up.'),
    ('SQLite database locked error',
     'Stop ALL backend instances. Only one uvicorn process should be running at a time.'),
]
for problem, solution in problems:
    story.append(Paragraph(f'Problem: {problem}', S['warning']))
    story.append(Paragraph(f'Solution: {solution}', S['body']))
    story.append(Spacer(1, 0.15*cm))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════
# SECTION 13 — ARCHITECTURE REFERENCE
# ══════════════════════════════════════════════════════════════════════
story.append(section_header(13, 'Project Architecture Reference'))
story.append(hr(C_ACCENT, 1))

story.append(Paragraph('13.1  Agent Pipeline (Data Flow)', S['h2']))
arch_text = [
    '[ User: Enter target domain in dashboard ]',
    '              |',
    '              v',
    '[ FastAPI Backend — POST /api/v1/scans ]',
    '              |  (Background Task)',
    '              v',
    '+--- SCOUT AGENT ---------------------------------+',
    '|  1. DNS subdomain brute-force (50+ subdomains)  |',
    '|  2. Certificate Transparency (crt.sh)           |',
    '|  3. Resolve hostnames to IP addresses           |',
    '|  4. TCP port scan (18 common ports)             |',
    '|  5. Shodan API enrichment (if key set)          |',
    '+-------------------------------------------------+',
    '              |  Assets[]',
    '              v',
    '+--- ANALYST AGENT -------------------------------+',
    '|  1. Map each asset to CVE threat database       |',
    '|  2. HTTP security header checks                 |',
    '|  3. TLS/SSL analysis                            |',
    '|  4. Compute per-asset risk scores               |',
    '|  5. Overall 0-100 risk score                    |',
    '+-------------------------------------------------+',
    '              |  Vulnerabilities[] + RiskScore',
    '              v',
    '+--- ORACLE AGENT --------------------------------+',
    '|  1. OpenAI GPT (if API key) or built-in engine  |',
    '|  2. Executive summary (for management)          |',
    '|  3. Technical analysis (for security team)      |',
    '|  4. Threat actor mapping                        |',
    '|  5. Prioritized remediation plan                |',
    '+-------------------------------------------------+',
    '              |  Report{}',
    '              v',
    '[ React Dashboard — live display ]',
]
story.append(code_block(*arch_text))

story.append(Paragraph('13.2  File Structure', S['h2']))
structure = [
    'sentinel/',
    '├── backend/',
    '│   ├── agents/',
    '│   │   ├── scout_agent.py    # Asset discovery',
    '│   │   ├── analyst_agent.py  # CVE correlation',
    '│   │   └── oracle_agent.py   # AI report generation',
    '│   ├── api/routes.py         # REST endpoints',
    '│   ├── models/               # SQLAlchemy DB models',
    '│   ├── db/database.py        # Async DB session',
    '│   ├── core/config.py        # Environment settings',
    '│   ├── main.py               # FastAPI application',
    '│   ├── requirements.txt      # Python dependencies',
    '│   └── .env.example          # Environment template',
    '├── frontend/',
    '│   ├── src/',
    '│   │   ├── pages/            # Dashboard, Scans, Assets, Vulns, Reports, Activity',
    '│   │   ├── components/       # Reusable React components',
    '│   │   └── utils/            # API client, helper functions',
    '│   ├── package.json          # Node dependencies',
    '│   └── vite.config.js        # Vite + proxy config',
    '├── docker-compose.yml        # One-command deployment',
    '└── README.md',
]
story.append(code_block(*structure))

story.append(Paragraph('13.3  API Endpoints Reference', S['h2']))
api_data = [
    ['Method', 'Endpoint',               'Description'],
    ['POST',   '/api/v1/scans',          'Create new scan (starts pipeline)'],
    ['GET',    '/api/v1/scans',          'List all scans'],
    ['GET',    '/api/v1/scans/{id}',     'Get scan with assets, vulns, report'],
    ['DELETE', '/api/v1/scans/{id}',     'Delete a scan'],
    ['GET',    '/api/v1/stats',          'Dashboard statistics'],
    ['GET',    '/health',                'Backend health check'],
    ['GET',    '/docs',                  'Swagger interactive API docs'],
]
api_table = Table(api_data, colWidths=[2*cm, 5.5*cm, 7.5*cm],
    style=TableStyle([
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
        ('FONTNAME',     (1,1), (1,-1),  'Courier'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('BACKGROUND',   (0,0), (-1,0),  C_HEADER),
        ('TEXTCOLOR',    (0,0), (-1,0),  C_WHITE),
        ('TEXTCOLOR',    (0,1), (0,-1),  colors.HexColor('#0070c0')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [C_WHITE, C_SURFACE]),
        ('BOX',          (0,0), (-1,-1), 0.5, C_BORDER),
        ('INNERGRID',    (0,0), (-1,-1), 0.3, C_BORDER),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
    ])
)
story.append(api_table)
story.append(Spacer(1, 0.6*cm))
story.append(hr(C_ACCENT, 1))
story.append(Paragraph(
    'Project Sentinel — Final Year Engineering Project  |  '
    'Document Version 1.0  |  All agents: Scout · Analyst · Oracle',
    sty('footer', fontSize=8, fontName='Helvetica', textColor=C_MUTED, alignment=TA_CENTER)
))

doc.build(story)
print("PDF generated successfully!")
