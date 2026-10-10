#!/usr/bin/env python3
"""Build the hand-designed, self-contained profile artwork. Python 3.11+, no packages."""

from pathlib import Path
import xml.etree.ElementTree as ET

from svg_design import BLUE, BORDER, HIGHLIGHT, MUTED, SURFACE, TEXT
from svg_design import circle, label, line, node, packet, path, rect, svg, text

ROOT = Path(__file__).resolve().parents[1]


def static_version(content):
    """An explicit picture source also covers browsers ignoring image media queries."""
    namespace = "{http://www.w3.org/2000/svg}"
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root = ET.fromstring(content)
    for parent in root.iter():
        for child in list(parent):
            if child.tag == namespace + "style" or child.attrib.get("class") == "motion":
                parent.remove(child)
        parent.attrib.pop("class", None)
    root.find(namespace + "title").text += " — static edition"
    description = root.find(namespace + "desc")
    description.text = description.text.replace(" A calm fourteen-second animation follows one request cycle.", "") + " Static edition without animation."
    return ET.tostring(root, encoding="unicode") + "\n"


def save(name, content):
    file = ROOT / "assets" / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")


def hero(mobile=False):
    w, h = (480, 800) if mobile else (1280, 480)
    s = f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#grid)"/>'
    s += f'<ellipse cx="{340 if mobile else 1030}" cy="{530 if mobile else 190}" rx="340" ry="300" fill="url(#light)"/>'
    x = 28 if mobile else 48
    s += line(x, 37, x + 25, 37, BLUE, 3) + label(x + 38, 42, "ENGINEERING LAB / 001", 13 if mobile else 15)
    if not mobile:
        s += label(1230, 42, "SYSTEMS IN MOTION", 13).replace('x="1230"', 'x="1230" text-anchor="end"')
    name_size = 57 if mobile else 86
    s += text(x - 3, 127 if mobile else 147, "SHILADITYA", name_size, weight=600, spacing=-3)
    s += text(x - 3, 195 if mobile else 246, "MAJUMDER", name_size, weight=600, spacing=-3)
    s += text(x, 238 if mobile else 294, "Backend Software Engineer", 23 if mobile else 26, HIGHLIGHT, 400, spacing=-.3)
    lines = ["Building reliable systems.", "Designing for scale.", "Engineering for the real world."]
    for i, value in enumerate(lines):
        s += text(x, (276 if mobile else 337) + 26 * i, value, 20 if mobile else 22, MUTED)
    if not mobile:
        s += rect(680, 63, 552, 360, fill="#0C1524", radius=8)
        s += line(638, 77, 638, 412, BORDER)
    # An intentional vertical spine with synchronous data branches and async delivery.
    ox, oy = (8, 387) if mobile else (708, 90)
    s += f'<g transform="translate({ox} {oy})">'
    s += label(0 if not mobile else 20, -13, "REQUEST / RESPONSE / ASYNC", 12)
    routes = [
        ("M144 36V56", .025, .09),
        ("M144 96V116", .13, .20),
        ("M244 140H324", .24, .30),
        ("M324 149H244", .34, .40),
        ("M244 157H280V203H324", .44, .50),
        ("M324 212H271V168H244", .52, .57),
        ("M144 174V208", .61, .67),
        ("M144 248V274", .70, .76),
        ("M133 116V96", .78, .84),
        ("M133 56V36", .87, .94),
    ]
    for d, _, _ in routes:
        s += path(d, BLUE if "144" in d else BORDER, 1.5, extra='marker-end="url(#arrow)"')
    s += node(70, 0, 148, 36, "CLIENT", size=16)
    s += node(44, 56, 200, 40, "API GATEWAY", size=16)
    s += node(44, 116, 200, 58, "FASTAPI", "request processing", True, 18)
    s += node(324, 116, 140, 50, "POSTGRESQL", size=15)
    s += node(324, 185, 140, 42, "REDIS", size=16)
    s += node(44, 208, 200, 40, "RABBITMQ", size=16)
    s += node(44, 274, 200, 54, "CELERY WORKERS", "background tasks", size=15)
    s += circle(224, 134, 3, HIGHLIGHT, 'class="process"')
    s += circle(224, 290, 3, HIGHLIGHT, 'class="process-worker"')
    s += label(259, 256, "PUBLISH / DELIVER", 10)
    s += label(259, 307, "COMPLETE", 10)
    for d, start, end in routes:
        s += packet(d, start, end)
    s += '</g>'
    if mobile:
        s += line(28, 757, 452, 757) + label(28, 782, "ARCHITECTURE STUDY / ILLUSTRATIVE", 11)
    else:
        s += line(48, 434, 1232, 434)
        s += label(48, 460, "PYTHON / APIs / DISTRIBUTED SYSTEMS", 13)
        s += text(1232, 460, "ARCHITECTURE STUDY · ILLUSTRATIVE", 13, MUTED, mono=True, anchor="end")
    return svg(w, h, "Shiladitya Majumder — Systems in Motion", "Backend software engineer. Building reliable systems. Designing for scale. Engineering for the real world. Illustrative client to gateway to FastAPI architecture, with PostgreSQL and Redis interactions, RabbitMQ delivery to Celery workers, and a returning response. A calm fourteen-second animation follows one request cycle.", s, True)


def practice(mobile=False):
    w, h = (480, 518) if mobile else (1000, 334)
    s = label(28, 35, "EXPERIENCE / ENGINEERING PRACTICE", 12)
    s += line(28, 55, w - 28, 55)
    s += text(28, 143 if mobile else 172, "5+", 80 if mobile else 104, weight=500, spacing=-6)
    if mobile:
        s += text(191, 107, "Years of experience", 22, weight=500)
        s += text(191, 137, "Python backend engineering", 16, MUTED)
        s += line(28, 173, 452, 173)
        sx, sy, gap = 28, 210, 98
    else:
        s += text(32, 215, "Years of experience", 23, weight=500)
        s += text(32, 246, "Python backend engineering", 17, MUTED)
        s += line(309, 80, 309, 293)
        sx, sy, gap = 347, 106, 78
    strengths = [
        ("API architecture", "Clear contracts. Deliberate service boundaries."),
        ("Distributed workflows", "Messaging, background processing, reliable retries."),
        ("Database engineering", "PostgreSQL, query optimization, data consistency."),
    ]
    for i, (title, subtitle) in enumerate(strengths):
        y = sy + i * gap
        s += label(sx, y, f"0{i+1}", 13)
        s += text(sx + 43, y + 1, title, 24 if mobile else 27, weight=500, spacing=-.5)
        if mobile:
            split = [
                ["Clear contracts.", "Deliberate service boundaries."],
                ["Messaging & background processing.", "Dependable retries."],
                ["PostgreSQL & query optimization.", "Consistency under concurrency."],
            ][i]
            for j, value in enumerate(split):
                s += text(sx + 43, y + 29 + 23 * j, value, 17, MUTED)
        else:
            s += text(sx + 43, y + 29, subtitle, 18, MUTED)
        if i < 2:
            s += line(sx + 43, y + (72 if mobile else 49), w - 28, y + (72 if mobile else 49))
    return svg(w, h, "Experience and engineering practice", "5+ years of experience in Python backend engineering. API architecture: clear contracts and service boundaries. Distributed workflows: messaging, background processing and dependable retries. Database engineering: PostgreSQL, query optimization and consistency under concurrency. Qualitative strengths from the professional biography, not performance measurements.", s)


LAYERS = [
    ("APPLICATION", ["Python", "FastAPI", "Django", "Django REST Framework"], "API contracts & services"),
    ("DATA", ["PostgreSQL", "MySQL", "Redis"], "Persistence & caching"),
    ("MESSAGING", ["RabbitMQ", "Celery"], "Events & background work"),
    ("INFRASTRUCTURE", ["AWS", "Docker", "Linux", "Nginx"], "Deployment & operations"),
    ("ENGINEERING", ["SQLAlchemy", "Pydantic", "Git"], "Models, validation & versioning"),
]


def ecosystem(mobile=False):
    w, h = (480, 842) if mobile else (1000, 524)
    s = label(28, 34, "TECHNOLOGY / RELATIONSHIP MAP", 12)
    s += line(28, 54, w - 28, 54)
    if not mobile:
        s += path('M220 101V439', BLUE, 1.5)
    for i, (name, technologies, purpose) in enumerate(LAYERS):
        y = 82 + i * (144 if mobile else 80)
        if mobile:
            s += label(28, y, f"0{i+1} / {name}", 13)
            s += text(28, y + 25, purpose, 17, MUTED)
            for j, tech in enumerate(technologies):
                nx, ny = 28 + (j % 2) * 218, y + 40 + (j // 2) * 43
                s += node(nx, ny, 208, 36, tech, accent=(i == 0 and j == 1), size=15 if len(tech) > 16 else 18)
            if i < 4:
                s += path(f'M28 {y+128}H452', BORDER, 1)
        else:
            s += label(28, y + 17, name, 13)
            s += text(28, y + 42, purpose.split(' & ')[0], 14, MUTED)
            s += circle(220, y + 22, 4) + line(220, y + 22, 252, y + 22, BLUE)
            count = len(technologies)
            nw = (716 - (count - 1) * 14) / count
            for j, tech in enumerate(technologies):
                nx = 252 + j * (nw + 14)
                if tech == "Django REST Framework":
                    s += node(nx, y - 5, nw, 54, "Django REST", "Framework", size=17)
                else:
                    s += node(nx, y, nw, 44, tech, accent=(i == 0 and j == 1), size=18)
            if i < 4:
                s += line(28, y + 64, 972, y + 64)
    s += text(28, h - 34, "Conceptual layers; technologies used across different projects.", 13 if mobile else 14, MUTED)
    s += text(28, h - 14, "Connections show engineering relationships, not a deployment.", 13 if mobile else 14, MUTED)
    return svg(w, h, "Engineering technology ecosystem", "Application: Python, FastAPI, Django, Django REST Framework. Data: PostgreSQL, MySQL, Redis. Messaging: RabbitMQ and Celery. Infrastructure: AWS, Docker, Linux, Nginx. Engineering: SQLAlchemy, Pydantic, Git. Conceptual layers across different projects, not a single production deployment.", s)


PROJECTS = {
    "visscan": ("01 / DOCUMENT INTELLIGENCE", [("Document", "PDF / DOCX / image"), ("Extract", "text / OCR"), ("OpenAI", "structured JSON"), ("MiniLM", "resume + job data"), ("Match", "score + highlights")], "VERIFIED FLOW / JOB DESCRIPTION IS PARSED SEPARATELY"),
    "fastapi-auth": ("02 / AUTHENTICATION FOUNDATION", [("Credentials", "email + password"), ("Auth service", "user verification"), ("JWT", "access + refresh"), ("Role checks", "dependencies"), ("Endpoints", "SQLAlchemy data")], "LOGIN ISSUES TOKENS / PROTECTED REQUESTS CHECK IDENTITY & ROLE"),
    "django-rest-auth": ("03 / PERMISSIONED DATA FLOW", [("Request", "bearer token"), ("SimpleJWT", "authentication"), ("Permissions", "access checks"), ("DRF", "view + serializer"), ("ORM", "SQLite default")], "PROTECTED CRUD FLOW / SERIALIZER VALIDATION ON WRITES"),
}


def project(name, mobile=False):
    heading, nodes, note = PROJECTS[name]
    w, h = (480, 432) if mobile else (1000, 188)
    s = label(28, 32, heading, 12)
    s += line(28, 49, w - 28, 49)
    if mobile:
        # Reading order snakes across pairs, with explicit directional connectors.
        positions = [(28, 78), (254, 78), (254, 183), (28, 183), (28, 288)]
        routes = ['M226 111H250', 'M353 144V179', 'M254 216H230', 'M127 249V284']
    else:
        positions = [(28 + i * 194, 73) for i in range(5)]
        routes = [f'M{204+i*194} 106H{218+i*194}' for i in range(4)]
    for route in routes:
        s += path(route, BLUE, 1.5, 'marker-end="url(#arrow)"')
    for i, ((title, subtitle), (x, y)) in enumerate(zip(nodes, positions)):
        s += node(x, y, 198 if mobile else 176, 66, title, subtitle, i == 2, 19)
    if mobile:
        s += text(254, 311, "SCHEMATIC", 13, HIGHLIGHT, mono=True)
        s += text(254, 336, "Source-informed flow", 14, MUTED)
        parts = {
            'visscan': ['Job description parsed separately;', 'resume and job data enter matching.'],
            'fastapi-auth': ['Login issues tokens; protected requests', 'check identity and role.'],
            'django-rest-auth': ['Protected CRUD flow; serializer', 'validation runs on writes.'],
        }[name]
        for i, value in enumerate(parts):
            s += text(28, 391 + i * 20, value, 14, MUTED)
    else:
        s += text(28, 166, note, 12, MUTED, mono=True, spacing=.3)
    return svg(w, h, heading, "Simplified source-informed flow: " + " → ".join(f"{a} ({b})" for a, b in nodes) + ". " + note + ". Represents implemented code paths, not a production or security audit.", s)


def terminal(mobile=False):
    w, h = (480, 369) if mobile else (1000, 223)
    s = label(28, 32, "LAB NOTES / PERSONAL SIGNATURE", 12) + line(28, 50, w - 28, 50)
    s += text(28, 82, "$ whoami", 17, HIGHLIGHT, mono=True)
    s += text(28, 112, "Shiladitya Majumder", 23, weight=600)
    s += text(28, 137, "Backend Software Engineer", 17, MUTED)
    x, y = (28, 183) if mobile else (450, 82)
    s += text(x, y, "$ engineering.focus", 17, HIGHLIGHT, mono=True)
    for i, v in enumerate(["> Reliable APIs", "> Distributed systems", "> Database performance", "> Scalable architecture"]):
        s += text(x, y + 27 + i * 22, v, 17, MUTED, mono=True)
    my = 320 if mobile else 182
    s += text(28, my, "$ mission", 17, HIGHLIGHT, mono=True)
    s += text(28, my + 29, "Build. Optimize. Scale. Repeat.", 19, weight=500)
    s += rect(307, my + 14, 8, 17, HIGHLIGHT, HIGHLIGHT, 0, 'class="cursor"')
    return svg(w, h, "Lab notes — personal signature", "whoami: Shiladitya Majumder, Backend Software Engineer. Engineering focus: reliable APIs, distributed systems, database performance, scalable architecture. Mission: Build. Optimize. Scale. Repeat.", s, True)


def footer(mobile=False):
    w, h = (480, 191) if mobile else (1000, 161)
    s = path(f'M28 34H{w//2-25}l13 -12h24l13 12H{w-28}', BORDER)
    s += circle(w // 2, 22, 3)
    s += label(28, 67, "THE NEXT SYSTEM STARTS WITH A CONVERSATION.", 10 if mobile else 13)
    if mobile:
        s += text(28, 109, "Let’s build something", 32, weight=500, spacing=-.8)
        s += text(28, 145, "reliable.", 32, HIGHLIGHT, weight=500, spacing=-.8)
    else:
        s += text(28, 111, "Let’s build something reliable.", 44, weight=500, spacing=-1.3)
    s += label(28, h - 19, "SHILADITYA MAJUMDER / ENGINEERING LAB", 11)
    return svg(w, h, "Let's build something reliable.", "The next system starts with a conversation. Shiladitya Majumder — Engineering Lab. Contact links follow in the README.", s)


def main():
    for mobile in (False, True):
        suffix = "-mobile" if mobile else ""
        for folder, name, make in [("hero", "hero", hero), ("dashboard", "engineering-practice", practice), ("diagrams", "ecosystem", ecosystem), ("terminal", "lab-notes", terminal), ("footer", "footer", footer)]:
            content = make(mobile)
            save(f"{folder}/{name}{suffix}.svg", content)
            if name in {"hero", "lab-notes"}:
                save(f"{folder}/{name}{suffix}-static.svg", static_version(content))
        for name in PROJECTS:
            save(f"diagrams/{name}{suffix}.svg", project(name, mobile))
    print("Generated 20 self-contained SVG assets, including explicit static motion fallbacks.")


if __name__ == "__main__":
    main()
