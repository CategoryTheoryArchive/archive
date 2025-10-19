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

    for items in data.values():
        for item in items:
            insert_id(item["id"], item)

    resources = data["resources"]
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
            link = None
            path = "resources/" + resource["id"] + ".pdf"
            if Path(path).is_file():
                link = "https://github.com/CategoryTheoryArchive/archive/blob/main/" + unicodedata.normalize("NFC", path)
            out.write("| " + ("c. " if circa else "") + year + " | " + resource.get("title", "") + " | " + authors + " | " + ("[" + resource["id"] + ".pdf](" + link + ")" if link is not None else "*Missing*") + " |")
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
            if "venue" in resource:
                kind = "proceedings"
                entry.append(["venue", ids[resource["venue"]]["name"]])
            if "book" in resource:
                kind = "incollection"
                entry.append(["booktitle", resource["book"]])
            if "pages" in resource:
                pages = resource["pages"]
                entry.append(["pages", str(pages[0]) + "--" + str(pages[1])])
            entries.append("@" + kind + "{" + resource["id"] + ",\n" + ",\n".join(map(lambda field: "  " + field[0] + "={" + field[1] + "}", entry)) + "\n}")
        out.write("\n\n".join(entries) + "\n")
