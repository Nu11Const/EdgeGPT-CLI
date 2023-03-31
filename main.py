import asyncio
from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markdown import Markdown
from EdgeGPT import Chatbot, ConversationStyle
import rich
from rich.traceback import install
from rich.live import Live
import websockets
import json
console = Console()
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
install()
style=ConversationStyle.balanced

def create_session() -> PromptSession:
    return PromptSession(history=InMemoryHistory())
async def get_input_async(
    session: PromptSession = None,
    completer: WordCompleter = None,
) -> str:
    """
    Multiline input function.
    """
    return await session.prompt_async(
        completer=completer,
        multiline=True,
        auto_suggest=AutoSuggestFromHistory(),
    )
n = 0
async def api(text):
    try:
        wrote = 0
        md = Markdown("")
        global n
        n = n+1
        if n >= 21:
            console.print("Exceeded conversation limit!")
            bot.reset()
            console.log("Reset successfly.")
            print()
        with Live(md, auto_refresh=False) as live:
            print("🤖 \033[32mBing\033[0m "+"("+str(n)+"/20"+"):")
            async for final, response in bot.ask_stream(
                    prompt=text,
                    conversation_style=style):
                if not final:
                    if wrote > len(response):
                        print(md)
                        print(Markdown("***Bing撤销了响应。***"))
                    wrote = len(response)
                    md = Markdown(response)
                    live.update(md, refresh=True)
                else:
                    suggestedResponses = response["item"]["messages"][1]["suggestedResponses"]
                    import json
                    with open("log.json","w") as f:
                        f.write(json.dumps(suggestedResponses))
                    for text in suggestedResponses:
                        md = Markdown(md.markup+"\n - "+text["text"])
                    live.update(md,refresh=True)
    except TimeoutError as err:
        console.print("访问超时，请检查您是否打开IPV6!",style="red")
        console.log(err)
    except Exception as err:
        console.print("未知错误",style="red")
        console.log(err)
    await bot.close()


async def main():
    title = Markdown(
        "# Welcome to the EdgeGPT-Cli-Demo [View](https://vmtask.icu) ## Use `!exit` to exit,`!reset` to reset the chatbot.")
    console.print(title)
    session = create_session()
    import os
    if not(os.path.exists("cookies.json")):
        console.print("[bold green]? [/] [green]Please input your Cookies:[/] ")
        cookie = await get_input_async(session=session)
        with open("cookies.json","w") as f:
            f.write(cookie)
    global bot
    bot = Chatbot(cookiePath='./cookies.json')
    global style
    while 1:
        try:
            console.print("[bold green]? [/] [green]You:[/] ")
            text = await get_input_async(session=session)
            if (text == "!exit"):
                import sys
                sys.exit()
            elif (text == "!reset"):
                await bot.reset()
            elif(text == "!b"):
                style = ConversationStyle.balanced
            elif(text == "!c"):
                style = ConversationStyle.creative
            elif(text == "!p"):
                style = ConversationStyle.precise
            else:
                await api(text)
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    asyncio.run(main())
