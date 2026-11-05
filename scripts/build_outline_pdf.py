"""Build the capabilities outline + draft PDF (outline structure with the README content filled in)."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = ROOT / "Brendan Stewart Capabilities Outline and Draft.pdf"

HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Brendan Stewart - Capabilities Outline and Draft</title>
<style>
@page { size: Letter; margin: 1in; }
* { box-sizing: border-box; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.38; color: #000; margin: 0; }
a { color: #1155cc; }
p { margin: 0 0 9pt; }
h2 { font-size: 17pt; margin: 22pt 0 10pt; }
.sec { margin: 0 0 14pt; }
.st { font-weight: bold; font-size: 11.5pt; margin: 0 0 4pt; break-after: avoid; }
ol { margin: 0; padding-left: 28pt; }
ol > li { margin: 0 0 8pt; padding-left: 4pt; }
ol > li > .lbl { font-weight: bold; }
.c { margin: 3pt 0 0; padding-left: 9pt; border-left: 2px solid #7c5cff; }
.c p { margin: 0 0 5pt; }
.c ul { margin: 2pt 0 5pt; padding-left: 16pt; }
.c li { margin: 0 0 2pt; }
.k { font-weight: bold; }
table { border-collapse: collapse; width: 100%; margin: 3pt 0 6pt; font-size: 9.5pt; }
th, td { border: 1px solid #999; padding: 3pt 6pt; text-align: left; vertical-align: top; }
th { background: #f1f1f1; }
li, tr { break-inside: avoid; }
.insp > li { margin-bottom: 6pt; }
.insp ol { list-style: lower-alpha; padding-left: 30pt; margin-top: 2pt; }
</style></head><body>

<p>Brendan Stewart<br>GIT 413<br>Capabilities Outline and Draft</p>
<p>GitHub account:<br><a href="https://github.com/hl2rs">https://github.com/hl2rs</a></p>

<h2>Outline:</h2>
<p>Purpose:<br>Showcase my background and inspirations as a full-stack software engineer and architect by
showcasing a few projects, mentioning skillset, my goals, work experience, and more that would be relevant to an
employer or person viewing a repo. In each section have either borders with color or solid color with left and
right styling with image included.</p>

<div class="sec"><p class="st">I. Header and Introduction</p>
<ol>
<li><span class="lbl">Name and Title</span>
  <div class="c"><p>Brendan Stewart, Software Engineer &amp; Architect<br>
  Studio City, CA &nbsp;|&nbsp; Logitech IT Tiger Team &nbsp;|&nbsp; ASU, 4.0 GPA</p></div></li>
<li><span class="lbl">Short welcome message</span>
  <div class="c"><p>&ldquo;Welcome! I design and build full-stack platforms, AI tools, and automation that move real
  businesses forward.&rdquo;</p></div></li>
<li><span class="lbl">Banner - Either a linear gradient or relevant picture</span>
  <div class="c"><p>An animated gradient banner (violet to blue to teal) with my name and title, a typing tagline that
  cycles through &ldquo;building full-stack platforms,&rdquo; &ldquo;shipping AI tools &amp; model routers,&rdquo;
  &ldquo;automating operations with data,&rdquo; and &ldquo;architecting software that scales,&rdquo; and a node
  graph of the systems I architect: Web UI, Node API, AI Router, Vision QA and Data Pipelines. A navigation bar links
  to About, Skills, Projects, Experience and Contact.</p></div></li>
</ol></div>

<div class="sec"><p class="st">II. About Me</p>
<ol>
<li><span class="lbl">Short Bio</span>
  <div class="c">
  <p>I am an engineer on Logitech&rsquo;s IT Software Development Tiger Team, building software with company-wide
  impact as well as leading data and software engineering for Ultimate Ears Pro.</p>
  <p>My path has been anything but typical. I joined Logitech in 2018 on the manufacturing floor and was promoted
  numerous times, through analyst and then engineering roles. Along the way I helped digitally transform businesses
  with heavy automation, better data accessibility, and thoughtful software.</p>
  <p>Shown beside an animated code-editor card listing my two teams (the IT Software Development Tiger Team and
  Ultimate Ears Pro), what I lead and build, and my stack.</p></div></li>
<li><span class="lbl">Education</span>
  <div class="c"><p>Arizona State University<br>B.S. Graphical Information Technology (Full Stack Web Development)<br>
  4.0 GPA &nbsp;|&nbsp; Graduating Fall 2026</p></div></li>
</ol></div>

<div class="sec"><p class="st">III. Technical Skills and Tools</p>
<ol>
<li><span class="lbl">Languages and frameworks</span>
  <div class="c">
  <p><span class="k">Languages:</span> JavaScript, Go, Java, C++, Python, SQL, HTML5, CSS3<br>
  <span class="k">Frontend:</span> React, Vue, Three.js, Tailwind CSS, Vite<br>
  <span class="k">Backend &amp; APIs:</span> Node.js, Express, Flask, REST APIs, Google Apps Script</p>
  <p>Presented as an animated icon board, one labeled row per category.</p></div></li>
<li><span class="lbl">Development practices and platforms</span>
  <div class="c">
  <p><span class="k">Development practices</span></p>
  <ul>
    <li><b>Full-stack architecture:</b> React/Vue front ends, Node.js &amp; Go services, REST APIs</li>
    <li><b>Automation-first:</b> Apps Script and API workflows that remove manual work</li>
    <li><b>Data-driven delivery:</b> pipelines from web store to BigQuery, Data Studio &amp; Tableau</li>
    <li><b>Cloud deployment</b> on Google Cloud Run &amp; Vercel</li>
    <li><b>Code review &amp; version control</b> with Git and GitHub</li>
    <li><b>Mentoring &amp; knowledge sharing</b> across teams and communities</li>
  </ul>
  <p><span class="k">Platforms</span><br>
  <span class="k">Data &amp; BI:</span> MongoDB, PostgreSQL, MySQL, SQL Server, Google Cloud SQL, BigQuery, Data Studio, Tableau<br>
  <span class="k">Cloud &amp; Platforms:</span> Google Cloud Run, Vercel, Shopify, Arduino, Git, GitHub<br>
  <span class="k">Design:</span> Photoshop, Illustrator, InDesign, Canva</p>
  <p><span class="k">Certifications</span></p>
  <table>
    <tr><th>Certification</th><th>Issuer</th></tr>
    <tr><td>AI Proficiency</td><td>Section &middot; ProfAI</td></tr>
    <tr><td>Programming in JavaScript</td><td>Meta</td></tr>
    <tr><td>Machine Learning: From Data to Decisions</td><td>MIT</td></tr>
    <tr><td>AI &amp; Law (with Honors)</td><td>Lund University</td></tr>
    <tr><td>Ask Questions to Make Data-Driven Decisions</td><td>Google</td></tr>
    <tr><td>Foundations: Data, Data, Everywhere</td><td>Google</td></tr>
  </table></div></li>
</ol></div>

<div class="sec" style="break-before:page"><p class="st">IV. Featured Projects</p>
<p style="margin-bottom:5pt; break-after:avoid">Each project is a full-width gradient card with an animated mock of the product on the
right, alternating between dark and light cards.</p>
<ol>
<li><span class="lbl">Web Auditor</span>
  <div class="c">
  <p><span class="k">Full-stack website crawler &amp; auditor.</span> Crawls an entire website and audits every page for
  dead links, security gaps, accessibility, content quality and live JavaScript errors, with a real-time dashboard
  and PDF reports.</p>
  <p><span class="k">Built with:</span> Python, Flask, Playwright, asyncio, Tailwind<br>
  <span class="k">Status:</span> Open source &mdash; <a href="https://github.com/hl2rs/Web-Auditor">https://github.com/hl2rs/Web-Auditor</a></p>
  <p>Card style: light, with a dark animated audit-dashboard mock (crawl progress, issue counts, findings list).</p></div></li>
<li><span class="lbl">Traveler</span>
  <div class="c">
  <p><span class="k">Plan an entire trip from a single prompt.</span> An all-in-one AI travel planning assistant that
  turns one prompt into day-by-day itineraries, budgets, and personalized recommendations, all in one place.</p>
  <p><span class="k">Highlights:</span> AI itineraries, budgets, recommendations<br>
  <span class="k">Status:</span> In active development &middot; Coming soon</p>
  <p>Card style: dark sunset gradient, with an animated trip-planner mock (prompt, day cards, route map, budget bar).</p></div></li>
</ol></div>

<div class="sec"><p class="st">V. Experience, Interests, and Goals</p>
<ol>
<li><span class="lbl">Jobs</span>
  <div class="c">
  <table>
    <tr><th>Role</th><th>Organization</th><th>Period</th></tr>
    <tr><td><b>Full Stack Developer</b><br>IT Software Development Tiger Team</td><td>Logitech</td><td>Dec 2018 &ndash; Present</td></tr>
    <tr><td><b>AI Champion</b><br>Driving AI adoption across the Southern California offices</td><td>Logitech &middot; Irvine &amp; Westlake Village</td><td>Current</td></tr>
    <tr><td><b>Technical Officer &amp; Mentor</b><br>Mentoring the next wave of developers</td><td>Google Developer Group</td><td>Apr 2026 &ndash; Present</td></tr>
  </table>
  <p><span class="k">Career climb:</span> Manufacturing (factory floor) &rarr; Analyst (data &amp; automation) &rarr;
  Full Stack Developer (UE Pro &amp; IT Tiger Team), shown as an animated staircase.</p>
  <p><span class="k">Impact highlights &mdash; led development of:</span></p>
  <ul>
    <li><b>Platforms:</b> a global on-demand shopping, warehouse &amp; logistics platform for employees and 3rd
    parties; financial operations, vendor assessment, gaming events &amp; competitions platforms and internal company tools</li>
    <li><b>AI:</b> a CLI and AI model router; a B2C web store AI bot and standalone interfaces; a modular, AI-powered
    fitment issue tool; automations from storage to an AI 3D modeling platform</li>
    <li><b>Vision &amp; Imaging:</b> QA computer vision models that detect defects down to the millimeter on clear
    surfaces; imaging algorithms and interfaces for operations &amp; manufacturing</li>
    <li><b>Security &amp; Data:</b> a self-healing web firewall; data pipelines from the web store to visualization tools</li>
  </ul>
  <p><span class="k">Awards &amp; honors</span></p>
  <table>
    <tr><th>Award</th><th>Organization</th><th>Year</th></tr>
    <tr><td>Employee of the Year</td><td>Logitech</td><td>2023</td></tr>
    <tr><td>Spotlight Award</td><td>Logitech</td><td>2022, 2023, 2024, 2026</td></tr>
    <tr><td>Top Volunteer</td><td>K9 Connection</td><td>2023</td></tr>
  </table></div></li>
<li><span class="lbl">Hobbies</span>
  <div class="c"><ul>
    <li><b>Traveling:</b> new places &amp; ideas</li>
    <li><b>Hiking:</b> trails &amp; summits</li>
    <li><b>Learning:</b> always leveling up</li>
  </ul>
  <p>Shown as three animated tiles: a globe with an orbiting plane, mountains with a rising sun, and an open book.</p></div></li>
<li><span class="lbl">Aspirations</span>
  <div class="c"><ul>
    <li>Grow into a software architect designing AI-native platforms at scale</li>
    <li>Keep mentoring the next wave of developers through Google Developer Groups</li>
    <li>Ship products that blend great design, data, and engineering</li>
  </ul></div></li>
</ol></div>

<div class="sec"><p class="st">VI. Contact</p>
<ol>
<li><span class="lbl">Email</span>
  <div class="c"><p><a href="mailto:hello@platmesh.com">hello@platmesh.com</a></p></div></li>
<li><span class="lbl">Personal website</span>
  <div class="c"><p>https://your-website.com (placeholder; to be replaced with the final address)</p>
  <p>Also linked: LinkedIn &mdash; <a href="https://www.linkedin.com/in/brendanstewart1">linkedin.com/in/brendanstewart1</a>
  &nbsp;|&nbsp; GitHub &mdash; <a href="https://github.com/hl2rs">github.com/hl2rs</a></p></div></li>
</ol></div>

<p class="st" style="margin-top:18pt">Three README Inspirations</p>
<ol class="insp">
<li><a href="https://github.com/MaxRohowsky">https://github.com/MaxRohowsky</a>
  <ol><li>This readme is awesome, well organized, and visually appealing. I love the use of tables to show projects
  and experience. Additionally the banner is relevant and looks great. I think the experience table is something
  I&rsquo;d like to include in a readme of my own.</li></ol></li>
<li><a href="https://github.com/supuna97">https://github.com/supuna97</a>
  <ol><li>The use of animated artwork and animated icons looks unique and pops to the eye. Having content and an
  animation side by side as a design looks nice. The icon animations is something I&rsquo;d like to include in my
  readme page to add a bit of life to something that would otherwise be static.</li></ol></li>
<li><a href="https://github.com/xiaoluoboding">https://github.com/xiaoluoboding</a>
  <ol><li>The gradient and contrast switching cards to show projects with images included on the right in the card
  is something I have not seen before and something I absolutely want to include. Seeing what the project output
  looks like is very useful and a great touch.</li></ol></li>
</ol>

</body></html>
"""


def main():
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "outline.html"
        page.write_text(HTML, encoding="utf-8")
        subprocess.run([
            EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}/profile",
            "--no-pdf-header-footer", f"--print-to-pdf={OUT}", page.as_uri(),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    sys.exit(main())
