

## \#\# README: 5-Step Run Instructions


# AI Agent: Bank Statement Parser Generator

This project contains an autonomous AI agent that automatically writes Python code to parse bank statement PDFs. Given a sample PDF and a corresponding CSV with the expected output, the agent will generate a custom parser file.

### Agent Architecture Diagram

The agent operates in a self-correcting loop, allowing it to refine its approach based on test results.

`[Setup & Read Files] -> [Plan Generation] -> [Code Generation] -> [Test Parser] -> [Success? (Yes -> END) | (No -> Refine Plan & Retry)]`

---

### 🚀 How to Run

Follow these 5 steps to run the agent and generate a parser for the ICICI bank statement.

**1. Clone the Repository**

```bash
git clone <your-repository-url>
cd ai-agent-challenge
````

**2. Set Up the Environment**

Create a virtual environment and install the required packages.

```bash
# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Configure the API Key**

The agent uses the Groq API for its intelligence. You must set your Groq API key as an environment variable.

```bash
export GROQ_API_KEY="PASTE_YOUR_GROQ_API_KEY_HERE"
```

**4. Run the Agent**

Execute the agent by specifying the target bank. The agent will read files from `data/icici/` and attempt to write a new parser.

```bash
python agent.py --target icici
```

**5. Verify the Output**

After a successful run, the agent will create a new file. Verify that the parser has been generated at the following path:

```
custom_parsers/icici_parser.py
```

```
```
