# HI-MAIA

HI-MAIA is implemented in this source code, along with the interface for user evaluation.

## Requirements

To run HI-MAIA, ensure your system meets the following prerequistes:

- Python 3.9
- CUDA 11.7

You can install the required libraries to operate HI-MAIA by using the following commands:

using Anaconda:

```bash
conda env create --file environment.yml
```

using pip:

```bash
pip install -r requirements.txt
```

## Configuration

The following environment variables must be set. Please configure them in `/.env` file.

```
SSL_CERT_PATH={Path to SSL fullchain}
SSL_KEY_PATH={Path to SSL privkey}
OPENAI_API_KEY={OpenAI API Key}
GOOGLE_TTS_API_KEY={Google Cloud Text-to-Speech API Key}
```

## How to Run

Once the requirements are satisfied, HI-MAIA can be launched with the following command:

```bash
python main.py --server_name={Host Address}
```
