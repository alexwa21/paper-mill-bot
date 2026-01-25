import os

# Create the hidden .streamlit folder
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

# Write the config to disable CORS and Email prompts
config_content = """
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
"""

with open(".streamlit/config.toml", "w") as f:
    f.write(config_content)

print("✅ Configuration fixed! You can now run the app.")