
# GitHub Sentiment Analysis and AI Review

This Python script analyzes GitHub issues and pull requests (PRs) from a specified repository, performs sentiment analysis on their titles and bodies, generates AI reviews using Gemini API, and plots sentiment analysis results.

## Features

- Fetches issues and PRs from a GitHub repository using the GitHub API.
- Performs sentiment analysis on each issue/PR title and body using TextBlob.
- Classifies sentiment into categories: "happy", "sad", or "neutral".
- Generates AI-powered reviews of issues/PRs using Gemini API.
- Posts AI reviews as comments on corresponding issues/PRs using GitHub CLI.
- Plots sentiment analysis results in a pie chart showing the distribution of sentiments.

## Requirements

- Python 3.x
- Required Python packages:
  - `requests`: for making HTTP requests to GitHub API.
  - `textblob`: for natural language processing tasks like sentiment analysis.
  - `google.generativeai` (assuming this is where the Gemini API client resides).
  - `matplotlib`: for plotting the sentiment analysis results.
  - `termcolor`: for colored output in the console.
  - `dotenv`: for loading environment variables from a `.env` file.
  
## Setup

1. Clone the repository and navigate into the directory:
   ```
   git clone https://github.com/your/repository.git
   cd repository
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following environment variables:
   ```
   GITHUB_TOKEN=<your GitHub personal access token>
   GEMINI_API_KEY=<your Gemini API key>
   ```

   Replace `<your GitHub personal access token>` with your GitHub token and `<your Gemini API key>` with your Gemini API key.

## Usage

Run the script from the command line with the following command:

```
python main.py <repo>
```

Replace `<repo>` with the GitHub repository in the format `owner/repository`.

## Example

To analyze issues and PRs from the repository `exampleuser/example-repo`, run:

```
python main.py exampleuser/example-repo
```

The script will fetch issues and PRs, perform sentiment analysis, generate AI reviews, and plot sentiment analysis results.
