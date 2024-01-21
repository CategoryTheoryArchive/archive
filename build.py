import json, shutil, unicodedata
from pathlib import Path

with open("archive.json") as file:
    data = None
    try:
        data = json.load(file)
    except:
        print("The JSON in archive.json is invalid.")

if data is not None:
    ids = {}

    def insert_id(id, value):
        if id in ids:
            print("Duplicate id")
            return
        ids[id] = value

    journals = data["journals"]
    for journal in journals:
        insert_id(journal["id"], journal)

    schools = data["schools"]
    for school in schools:
        insert_id(school["id"], school)

    authors = data["authors"]
    for author in authors:
        insert_id(author["id"], author)

    resources = data["resources"]
    for resource in resources:
        insert_id(resource["id"], resource)
    resources.sort(key = lambda resource: resource["date"])

    # Generate a table for the README.
    shutil.copyfile("README-template.md", "README.md")
    with open("README.md", "a") as out:
        out.write("\n")
        out.write("| " + " | ".join(["Year", "Title", "Authors", "Link"]) + " |\n")
        out.write("| " + " | ".join(["---"] * 4) + " |\n")
        for resource in resources:
            date = resource["date"]
            circa = date[-1] == "~"
            year = date.rstrip("~").split("-")[0]
            authors = ", ".join(map(lambda author : ids[author]["name"], resource["authors"]))
            link = ""
            path = "resources/" + resource["id"] + ".pdf"
            if Path(path).is_file():
                link = "https://github.com/CategoryTheoryArchive/archive/blob/main/" + unicodedata.normalize("NFC", path)
            out.write("| " + ("c. " if circa else "") + year + " | " + resource.get("title", "") + " | " + authors + " | " + "[" + resource["id"] + ".pdf](" + link + ") |")
            out.write("\n")

    # Generate a .bib file.
    with open("build/references.bib", "w") as out:
        entries = []
        for resource in resources:
            entry = []
            entry.append(["title", resource.get("title", "")])
            authors = " and ".join(map(lambda author : ids[author]["name"], resource["authors"]))
            entry.append(["author", authors])
            entry.append(["date", resource.get("date")])
            kind = "unpublished"
            if "journal" in resource:
                kind = "article"
                entry.append(["journal", ids[resource["journal"]]["name"]])
            if "school" in resource:
                kind = "phdthesis"
                entry.append(["school", ids[resource["school"]]["name"]])
            if "institution" in resource:
                kind = "techreport"
                entry.append(["institution", ids[resource["institution"]]["name"]])
            if "pages" in resource:
                pages = resource["pages"]
                entry.append(["pages", str(pages[0]) + "--" + str(pages[1])])
            entries.append("@" + kind + "{" + resource["id"] + ",\n" + ",\n".join(map(lambda field: "  " + field[0] + "={" + field[1] + "}", entry)) + "\n}")
        out.write("\n\n".join(entries) + "\n")
