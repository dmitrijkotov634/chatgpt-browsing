import time
from urllib.parse import urlparse

import openai
import requests
from bs4 import BeautifulSoup

from functions import Functions, Param

browsing = Functions()

openai.api_key = "sk-"

hrefs = []


@browsing
def browse(
        url: Param(str, "URL")
):
    """Open URL and get site text and available links"""
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    parse = urlparse(url)

    print(f"$ Open {url}")

    links = []
    for n, a in enumerate(soup.find_all('a', href=True)):
        link = a['href']
        if link.startswith("/"):
            link = f"{parse.scheme}://{parse.netloc}{link}"
        hrefs.append(link)
        links.append(f"Link №{len(hrefs)} - {a.text}")

    return ", ".join(links) + "\n" + soup.text


@browsing
def google(
        query: Param(str, "Search query")
):
    """Open google search"""
    return browse("https://www.google.com/search?q=" + query)


@browsing
def click_link(
        n: Param(int, "Link №")
):
    """Click on link"""
    print(f"$ Click on №{n}")
    return browse(hrefs[n])


messages = []

while True:
    messages.append({
        "role": "user",
        "content": input("> ")
    })

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=browsing.to_json(),
        function_call="auto",
    )

    message = response["choices"][0]["message"]
    messages.append(message)
    result = browsing.call_functions(message)

    if result:
        messages.append(result)

    while result is not None:
        last_request_time = time.time()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=messages,
            functions=browsing.to_json(),
            function_call="auto",
        )
        message = response["choices"][0]["message"]
        result = browsing.call_functions(message)
        if result:
            messages.append(result)
        request_sleep_time = 15 - (time.time() - last_request_time)
        if request_sleep_time > 0:
            time.sleep(request_sleep_time)

    print(message["content"])
