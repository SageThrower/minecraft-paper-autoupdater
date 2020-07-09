#!/usr/bin/python

from requests import get
from os import listdir, remove
from subprocess import call

MINECRAFT_VERSION = "1.16.1"
SCRIPT_FILE = "start.sh"
# If you need to edit the ram usage or the start script in any way you HAVE to edit the string below
#
# [paperFile] gets replaced with the correct latest downloaded paper jar
#
# Oh and also this is shell not bash, so it doesn't work on windows
# If you need windows support (Idk why) edit the name above to make it end in .bat (And also edit the script (duh))
START_SH_COMMAND = """
#!/bin/bash
java -Xmx2G -jar [paperFile] -nogui
""".strip()


def human_readable_size(size, decimal_places=0):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"


def download_paper(mc_version: str, paper_version: str, chunk_size: int = 16384, cool_alive_thing: bool = False) -> str:
    file_name = f"paper_{mc_version}_{paper_version}.jar"
    downloaded = 0
    with get(f"https://papermc.io/api/v1/paper/{mc_version}/{paper_version}/download", stream=True) as request:
        with open(file_name, "wb") as file:
            for chunk in request.iter_content(chunk_size=chunk_size):
                file.write(chunk)
                if cool_alive_thing:
                    downloaded += chunk_size
                    print(f"\rDownloading paper {mc_version} v{paper_version} (Downloaded {human_readable_size(downloaded, 2)})           ", end="")
    if cool_alive_thing:
        print()
    return file_name


if __name__ == '__main__':
    latest_version = str(get(f"https://papermc.io/api/v1/paper/{MINECRAFT_VERSION}").json()["builds"]["latest"])
    paper_jar_file = paper_jar_file[0] if (paper_jar_file := [file for file in listdir(".") if file.startswith(f"paper_{MINECRAFT_VERSION}_") and file.endswith(".jar")]) else "0 "
    if latest_version.isdigit() and int(latest_version) > int(paper_jar_file.replace(".jar", "").replace(f"paper_{MINECRAFT_VERSION}_", "")):
        print("Found new paper version!")
        downloaded_file_name = download_paper(MINECRAFT_VERSION, latest_version, 16384, True)
        try:
            remove(paper_jar_file)
        except FileNotFoundError:
            pass
        open(SCRIPT_FILE, "w").write(START_SH_COMMAND.replace("[paperFile]", downloaded_file_name))
    try:
        call(["./" + SCRIPT_FILE])
    except PermissionError:
        print(f"I do not have the permission to execute {SCRIPT_FILE}!\nPlease run \"chmod +x {SCRIPT_FILE}\"!")
