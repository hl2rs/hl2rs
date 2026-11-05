from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "README.docx"
FONT = "Arial"
BLACK = RGBColor(0, 0, 0)

doc = Document()
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(1)
sec.top_margin = sec.bottom_margin = Inches(1)

for name, size in [("Normal", 11), ("Title", 24), ("Heading 1", 16), ("Heading 2", 13), ("List Bullet", 11)]:
    st = doc.styles[name]
    st.font.name = FONT
    st.font.size = Pt(size)
    st.font.color.rgb = BLACK
    rpr = st.element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:eastAsia"), FONT)
    rpr.rFonts.set(qn("w:ascii"), FONT)
    rpr.rFonts.set(qn("w:hAnsi"), FONT)
    if name in ("Title", "Heading 1", "Heading 2"):
        st.font.bold = True

# Remove the bottom border the default Title style carries
ppr = doc.styles["Title"].element.get_or_add_pPr()
for b in ppr.findall(qn("w:pBdr")):
    ppr.remove(b)


def add_runs(p, text):
    for i, chunk in enumerate(text.split("**")):
        if chunk:
            p.add_run(chunk).bold = i % 2 == 1


def para(text="", after=6):
    p = doc.add_paragraph()
    add_runs(p, text)
    p.paragraph_format.space_after = Pt(after)
    return p


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    add_runs(p, text)
    p.paragraph_format.space_after = Pt(2)


def link(p, text, url):
    rid = p.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(u)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)


def h1(text):
    doc.add_heading(text, level=1)


def h2(text):
    doc.add_heading(text, level=2)


doc.add_paragraph("Brendan Stewart", style="Title")
para("**Software Engineer & Architect** — building full-stack platforms", after=2)
para("Studio City, CA | Logitech, IT Software Development Tiger Team | Arizona State University, 4.0 GPA", after=2)
para("I design and build full-stack platforms, AI tools, and automation that move real businesses forward.")
para("**Systems I architect:** Web UI (React, Vue); Node API (REST, Express); AI Router (LLMs, RAG, CLI); "
     "Vision QA (millimeter-level defects); Data Pipelines (BigQuery to BI)")

h1("About Me")
para("I am an engineer on Logitech's **IT Software Development Tiger Team**, building software with company-wide "
     "impact as well as leading data and software engineering for **Ultimate Ears Pro**.")
para("My path has been anything but typical. I joined Logitech in **2018 on the manufacturing floor** and was "
     "promoted numerous times, through **analyst** and then **engineering** roles. Along the way I helped digitally "
     "transform businesses with heavy automation, better data accessibility, and thoughtful software.")
para("**Education:** Arizona State University, B.S. Graphical Information Technology, Full Stack Web Development, "
     "4.0 GPA, graduating Fall 2026")

h1("Technical Skills & Tools")
for b in [
    "**Languages:** JavaScript, Go, Java, C++, Python, SQL, HTML5, CSS3",
    "**Frontend:** React, Vue, Three.js, Tailwind, Vite",
    "**Backend & APIs:** Node.js, Express, Flask, REST APIs, Apps Script",
    "**Data & BI:** MongoDB, PostgreSQL, MySQL, SQL Server, Cloud SQL, BigQuery, Data Studio, Tableau",
    "**Cloud & Platforms:** Cloud Run, Vercel, Shopify, Arduino, Git, GitHub",
    "**Design:** Photoshop, Illustrator, InDesign, Canva",
]:
    bullet(b)

h2("Development Practices")
for b in [
    "**Full-stack architecture:** React/Vue front ends, Node.js & Go services, REST APIs",
    "**Automation-first:** Apps Script and API workflows that remove manual work",
    "**Data-driven delivery:** pipelines from web store to BigQuery, Data Studio & Tableau",
    "**Cloud deployment** on Google Cloud Run & Vercel",
    "**Code review & version control** with Git and GitHub",
    "**Mentoring & knowledge sharing** across teams and communities",
]:
    bullet(b)

h2("Certifications")
for b in [
    "AI Proficiency Section, ProfAI",
    "Programming in JavaScript, Meta",
    "Machine Learning: From Data to Decisions, MIT",
    "AI & Law (with Honors), Lund University",
    "Ask Questions to Make Data-Driven Decisions, Google",
    "Foundations: Data, Data, Everywhere, Google",
]:
    bullet(b)

h1("Featured Projects")
h2("Web Auditor")
para("Full-stack website crawler & auditor. Crawls an entire site and audits every page for dead links, security "
     "gaps, accessibility, content quality and live JS errors, with a real-time dashboard and PDF reports.", after=2)
para("**Built with:** Python, Flask, Playwright, asyncio, Tailwind. Open source on GitHub.", after=2)
p = para("Source: ")
link(p, "https://github.com/hl2rs/Web-Auditor", "https://github.com/hl2rs/Web-Auditor")
h2("Traveler")
para("Plan an entire trip from a single prompt. An all-in-one AI travel planning assistant that turns one prompt "
     "into day-by-day itineraries, budgets, and personalized recommendations.", after=2)
para("**Features:** AI itineraries, budgets, recommendations. In active development.")

h1("Experience, Interests & Goals")
h2("Experience")
for b in [
    "**Full Stack Developer**, Logitech (IT Software Development Tiger Team), Dec 2018 – Present",
    "**AI Champion**, Logitech, Irvine & Westlake Village: driving AI adoption across the Southern California "
    "offices, Current",
    "**Technical Officer & Mentor**, Google Developer Group: mentoring the next wave of developers, "
    "Apr 2026 – Present",
]:
    bullet(b)

h2("Career Path (Dec 2018 – Present)")
for b in [
    "Manufacturing: factory floor",
    "Analyst: data & automation",
    "Full Stack Developer: UE Pro & IT Tiger Team",
]:
    bullet(b)

h2("Awards & Honors")
for b in [
    "**Employee of the Year**, 2023 (Logitech)",
    "**Spotlight Award**, 2022, 2023, 2024, 2026 (Logitech)",
    "**Top Volunteer**, 2023 (K9 Connection)",
]:
    bullet(b)

h2("Impact Highlights")
para("Led development of:", after=2)
for b in [
    "**Platforms:** global on-demand shopping, warehouse & logistics platform for employees and 3rd parties; "
    "financial operations, vendor assessment, gaming events & internal company tools",
    "**AI:** CLI and AI model router; B2C web store AI bot and standalone interfaces; modular AI-powered fitment "
    "issue tool; automations from storage to an AI 3D modeling platform",
    "**Vision & Imaging:** QA computer vision models that detect defects down to the millimeter on clear surfaces; "
    "imaging algorithms and interfaces for operations & manufacturing",
    "**Security & Data:** self-healing web firewall; data pipelines from the web store to visualization tools",
]:
    bullet(b)

h2("Goals")
for b in [
    "Grow into a software architect designing AI-native platforms at scale",
    "Keep mentoring the next wave of developers through Google Developer Groups",
    "Ship products that blend great design, data, and engineering",
]:
    bullet(b)

h2("Interests")
for b in ["**Traveling:** new places & ideas", "**Hiking:** trails & summits", "**Learning:** always leveling up"]:
    bullet(b)

h1("Contact")
para("Let's build something together. I'm always happy to talk about full-stack architecture, AI tooling, "
     "automation, or mentoring. Reach out anytime!")
p = para("Email: ", after=2)
link(p, "hello@platmesh.com", "mailto:hello@platmesh.com")
p = para("LinkedIn: ", after=2)
link(p, "https://www.linkedin.com/in/brendanstewart1", "https://www.linkedin.com/in/brendanstewart1")
p = para("GitHub: ", after=2)
link(p, "https://github.com/hl2rs", "https://github.com/hl2rs")
para("Website: https://your-website.com (placeholder, to be replaced)")
para("Thanks for stopping by!")

doc.save(OUT)
print("saved", OUT)
