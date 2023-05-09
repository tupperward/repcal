FROM faucet/python3

ENV 'DISCORD_WEBHOOK_URL'='https://discord.com/api/webhooks/1072769944556671047/Y8A8yYJ23B_nD9aFaoaNv-bHTjB0skUbs-VR4mkvTHTYMg-udi3uuRnLKWbc2fbG9Mef'
ENV 'REPCAL_DATA_URL'='https://repcal.tupperward.net/data'

COPY webhook.py .

RUN pip install discord

CMD ["python", "webhook.py"]