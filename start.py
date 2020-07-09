#!/usr/bin/python

from requests import get
from os import listdir, remove
from subprocess import call

# The version of minecraft to be downloaded (Check that paper supports the version first ;D)
MINECRAFT_VERSION = "1.16.1"
# The name of the script that will be created and ran
# Opted for this way mostly from familiarity and support for bukkits restart on crash script
#   (It should work for python files with #!/usr/bin/python but i really do not want to test that rn)
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


# Stolen from stackoverflow
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
            # Basically every chunk_size bytes that are downloaded the code inside the for is ran,
            #   saving those bytes to the file and also if console logging is enabled printing some info
            for chunk in request.iter_content(chunk_size=chunk_size):
                file.write(chunk)
                if cool_alive_thing:
                    downloaded += chunk_size
                    print(
                        f"\rDownloading paper {mc_version} v{paper_version} "
                        f"(Downloaded {human_readable_size(downloaded, 2)})   ",
                        end="")
    if cool_alive_thing:
        print()
    return file_name


def get_latest_version(minecraft_version: str) -> str:
    # Since requests is bugged af i need to request with "with" to avoid a memory leak
    with get(f"https://papermc.io/api/v1/paper/{minecraft_version}") as request:
        return str(request.json()["builds"]["latest"])


def get_latest_paper_supported_mc_version():
    with get("https://papermc.io/api/v1/paper") as request:
        return str(request.json()["versions"][0])


if __name__ == '__main__':
    latest_version = get_latest_version(MINECRAFT_VERSION)

    # Basically finds the paper jar file lastly downloaded using this script
    # If none are found the variable is set to "0"
    paper_jar_file = paper_jar_file[0] if (
        paper_jar_file := [file for file in listdir(".") if file.startswith(f"paper_{MINECRAFT_VERSION}_")
                           and file.endswith(".jar")]
    ) else "0"

    if (supp := get_latest_paper_supported_mc_version()) != MINECRAFT_VERSION:
        print(f"{supp} is now supported by paper!\n"
              f"I suggest changing the MINECRAFT_VERSION variable to that latest version to stay updated!")

    # Checks if it needs to update (If the latest version is greater than the local version)
    if latest_version.isdigit() and int(latest_version) > int(
            paper_jar_file.replace(".jar", "").replace(f"paper_{MINECRAFT_VERSION}_", "")):
        print("Found new paper version!")
        downloaded_file_name = download_paper(MINECRAFT_VERSION, latest_version, 16384, True)
        try:
            remove(paper_jar_file)
        except FileNotFoundError:
            pass

        # Writes to SCRIPT_FILE the START_SH_COMMAND with [paperFile] replaced to the correct jar filename
        open(SCRIPT_FILE, "w").write(START_SH_COMMAND.replace("[paperFile]", downloaded_file_name))
    try:
        call(["./" + SCRIPT_FILE])
    except PermissionError:
        # On the first on linux it might happen that the permission to run the file isn't present
        print(f"I do not have the permission to execute {SCRIPT_FILE}!\nPlease run \"chmod +x {SCRIPT_FILE}\"!")
