import argparse
import requests
from textblob import TextBlob
import google.generativeai as genai
import matplotlib.pyplot as plt
from termcolor import colored
from dotenv import load_dotenv
import os
import subprocess

# Load environment variables from .env file
load_dotenv()

# Function to fetch issues and PRs
def fetch_issues(repo, token):
    issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/issues?page={page}&state=all"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch issues: {response.status_code}")
            break
        page_issues = response.json()
        if not page_issues:
            break
        issues.extend(page_issues)
        page += 1
    return issues

# Function to perform sentiment analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Function to classify sentiment
def classify_sentiment(polarity):
    if polarity > 0.1:
        return "happy"
    elif polarity < -0.1:
        return "sad"
    else:
        return "neutral"

# Function to generate AI review using Gemini API
def generate_review(apikey, text):
    genai.configure(api_key=apikey)
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat()
    response = chat.send_message(f"Review this text like a senior developer: {text}")
    return response.text

# Function to post comment using GitHub CLI
def post_comment(repo, issue_number, comment):
    try:
        if len(comment) > 65536:
            comment = comment[:65536]  # Truncate comment if it's too long
        subprocess.run(["gh", "issue", "comment", str(issue_number), "--repo", repo, "--body", comment], check=True)
        print(colored(f"Comment posted successfully for issue/PR #{issue_number}.", "green"))
    except subprocess.CalledProcessError as e:
        print(colored(f"Failed to post comment for issue/PR #{issue_number}: {e}", "red"))

# Function to plot sentiment analysis results
def plot_sentiment(sentiments):
    labels = ['happy', 'sad', 'neutral']
    sizes = [sentiments.count('happy'), sentiments.count('sad'), sentiments.count('neutral')]
    colors = ['green', 'red', 'blue']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sentiment Analysis of GitHub Issues and PRs')
    plt.show()

# Main function
def main(repo):
    token = os.getenv('GITHUB_TOKEN')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not token or not gemini_api_key:
        print(colored("Please make sure GITHUB_TOKEN and GEMINI_API_KEY are set in the .env file.", "red"))
        return
    
    issues_and_prs = fetch_issues(repo, token)
    sentiments = []
    for item in issues_and_prs:
        item_type = 'PR' if 'pull_request' in item else 'Issue'
        title = item['title']
        body = item.get('body', '')
        body = '' if body is None else body
        text = title + " " + body
        sentiment_polarity = analyze_sentiment(text)
        sentiment = classify_sentiment(sentiment_polarity)
        sentiments.append(sentiment)
        colored_sentiment = colored(sentiment, 'green' if sentiment == 'happy' else 'red' if sentiment == 'sad' else 'blue')
        print(f"Type: {colored(item_type, 'cyan')}\nTitle: {colored(title, 'yellow')}\nSentiment: {colored_sentiment}\n")
    
    # Plot sentiment analysis results
    plot_sentiment(sentiments)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentiment analysis of GitHub issues and PRs with AI reviews")
    parser.add_argument("repo", help="GitHub repository in the format 'owner/repo'")
    
    args = parser.parse_args()
    main(args.repo)
