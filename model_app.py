import modal

app = modal.App(name="streamlit-salesbot")

image = modal.Image.debian_slim().pip_install(
    "streamlit", "transformers", "torch", "accelerate"
)

@app.function()
def run():
    import subprocess
    subprocess.run(["streamlit", "run", "/app/app.py"])
