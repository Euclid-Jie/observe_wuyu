# Observe Wuyu

## Setup Instructions

To set up this project properly, you need to:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Git Submodules
```bash
git submodule update --init --recursive
```

This will properly initialize the `AutoEmail` submodule which is required for email functionality.

### 3. Environment Configuration
Make sure you have the proper environment variables set up as defined in `config.py`. Create a `.env` file in the root directory if running locally.

## Usage

Run the main display script:
```bash
python display_bench_stats.py
```

## Troubleshooting

### ImportError: cannot import name 'AutoEmail' from 'AutoEmail'
This error occurs when:
1. Git submodules haven't been initialized (run `git submodule update --init --recursive`)
2. Dependencies haven't been installed (run `pip install -r requirements.txt`)

### Missing dotenv module
Install dependencies: `pip install -r requirements.txt`