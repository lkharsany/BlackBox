import requests

username = "discordbot"
password = "discordbot"
url = "https://courses.ms.wits.ac.za/moodle"
r = requests.get(
    f"{url}/login/token.php?username={username}&password={password}&service=moodle_mobile_app")
token = r.json()['token']
print(token)
