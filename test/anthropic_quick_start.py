import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    # api_key="",
)


def run():
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.0,
        system="You are a comedian. Respond with humour.",
        messages=[
            {"role": "user", "content": "How are you today?"}
        ]
    )

    print(message.content)


if __name__ == '__main__':
    run()
