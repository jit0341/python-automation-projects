from pathlib import Path
from core_agent_ready import process_invoice

INPUT_DIR = "input"

def agent_run():
    pdfs = list(Path(INPUT_DIR).glob("*.pdf"))

    if not pdfs:
        print("🤖 Agent idle – no invoices found")
        return

    for pdf in pdfs:
        print(f"🤖 Agent processing: {pdf.name}")
        process_invoice(str(pdf))

if __name__ == "__main__":
    agent_run()
