import argparse
import requests
from textblob import TextBlob
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
from openai import OpenAI
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from pyfiglet import Figlet

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client for MindsDB
mindsdb_client = OpenAI(
    api_key=os.getenv("MINDSDB_API_KEY"),
    base_url="https://llm.mdb.ai/"
)

# Function to fetch issues, pull requests, and comments from GitHub
def fetch_issues_and_comments(repo, token):
    issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/issues?page={page}&state=all"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            rprint(f"[red]Failed to fetch issues: {response.status_code}[/red]")
            break
        page_issues = response.json()
        if not page_issues:
            break
        issues.extend(page_issues)
        page += 1
    
    # Fetch comments for each issue and PR
    for issue in issues:
        comments_url = f"https://api.github.com/repos/{repo}/issues/{issue['number']}/comments"
        response = requests.get(comments_url, headers=headers)
        if response.status_code == 200:
            comments = response.json()
            issue['comments'] = [comment['body'] for comment in comments]
        else:
            issue['comments'] = []

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

# Function to generate AI review using MindsDB's Gwmini model
def generate_review(client, text):
    completion = client.chat.completions.create(
        model="claude-3-haiku",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Review this issue or pull request from github , and suggest the reply like a human: {text}"}
        ],
        stream=False
    )
    return completion.choices[0].message.content

# Function to plot sentiment analysis results
def plot_sentiment(sentiments):
    labels = ['happy', 'sad', 'neutral']
    sizes = [sentiments.count('happy'), sentiments.count('sad'), sentiments.count('neutral')]
    colors = ['green', 'red', 'blue']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sentiment Analysis of GitHub Issues and PRs')
    plt.show()

# Function to print detailed information using rich library
def print_detailed_info(item_type, title, sentiment, user, created_at, url, review, comments=None):
    table = Table(title="GitHub Issue/PR Details")
    table.add_column("Type", style="cyan", justify="left")
    table.add_column("Title", style="yellow", justify="left")
    table.add_column("Sentiment", justify="left")
    table.add_column("User", style="magenta", justify="left")
    table.add_column("Created at", style="white", justify="left")
    table.add_column("URL", style="blue", justify="left")
    table.add_row(item_type, title, sentiment, user, created_at, url)
    
    rprint(table)
    rprint(f"[green]AI Review:[/green]")
    rprint(review)
    
    if comments:
        rprint("[cyan]Comments:[/cyan]")
        for comment in comments:
            rprint(comment)
            rprint("-" * 80)

# Function to get plot only
def get_plot(repo):
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        rprint("[red]Please make sure GITHUB_TOKEN is set in the .env file.[/red]")
        return
    
    issues_and_prs = fetch_issues_and_comments(repo, token)
    sentiments = []
    for item in issues_and_prs:
        body = item.get('body', '') or ''
        text = item['title'] + " " + body
        sentiment_polarity = analyze_sentiment(text)
        sentiment = classify_sentiment(sentiment_polarity)
        sentiments.append(sentiment)
    
    # Plot sentiment analysis results
    plot_sentiment(sentiments)

# Function to generate review for a specific PR or issue
def get_review_for_item(repo, item_number):
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        rprint("[red]Please make sure GITHUB_TOKEN is set in the .env file.[/red]")
        return
    
    url = f"https://api.github.com/repos/{repo}/issues/{item_number}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        rprint(f"[red]Failed to fetch the issue/PR: {response.status_code}[/red]")
        return
    
    item = response.json()
    item_type = 'PR' if 'pull_request' in item else 'Issue'
    title = item['title']
    body = item.get('body', '') or ''
    text = title + " " + body
    sentiment_polarity = analyze_sentiment(text)
    sentiment = classify_sentiment(sentiment_polarity)
    user = item['user']['login']
    created_at = item['created_at']
    url = item['html_url']
    
    # Fetch comments for the specific issue/PR
    comments_url = f"https://api.github.com/repos/{repo}/issues/{item_number}/comments"
    response = requests.get(comments_url, headers=headers)
    if response.status_code == 200:
        comments = [comment['body'] for comment in response.json()]
    else:
        comments = []
    
    # Generate and display review using MindsDB
    review = generate_review(mindsdb_client, text)
    print_detailed_info(item_type, title, sentiment, user, created_at, url, review, comments)

# Function to display help and ASCII art logo
def display_help():
    f = Figlet(font='slant')
    logo = f.renderText('GitHub Sentiment Analysis')
    rprint(f"[cyan]{logo}[/cyan]")
    rprint("Welcome to GitHub Sentiment Analysis tool!")
    rprint("Usage:")
    rprint("python script.py owner/repo [--plot] [--review <item_number>]")
    rprint("")
    rprint("Commands:")
    rprint("--plot\t\t\t\t\t\tPlot sentiment analysis of all issues and PRs.")
    rprint("--review <item_number>\t\t\tGenerate sentiment analysis and AI review for a specific issue/PR.")
    rprint("")
    rprint("Examples:")
    rprint("python script.py user/repository --plot")
    rprint("python script.py user/repository --review 123")
    rprint("")

# Main function
def main(repo):
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        rprint("[red]Please make sure GITHUB_TOKEN is set in the .env file.[/red]")
        return
    
    issues_and_prs = fetch_issues_and_comments(repo, token)
    sentiments = []
    for item in issues_and_prs:
        item_type = 'PR' if 'pull_request' in item else 'Issue'
        title = item['title']
        body = item.get('body', '') or ''
        text = title + " " + body
        sentiment_polarity = analyze_sentiment(text)
        sentiment = classify_sentiment(sentiment_polarity)
        sentiments.append(sentiment)
        user = item['user']['login']
        created_at = item['created_at']
        url = item['html_url']
        
        # Fetch comments for the issue/PR
        comments = item.get('comments', [])
        
        # Generate and display review using MindsDB
        review = generate_review(mindsdb_client, text)
        print_detailed_info(item_type, title, sentiment, user, created_at, url, review, comments)
    
    # Plot sentiment analysis results
    plot_sentiment(sentiments)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentiment analysis of GitHub issues and PRs with AI reviews")
    parser.add_argument("repo", help="GitHub repository in the format 'owner/repo'")
    parser.add_argument("--plot", action="store_true", help="Only plot the sentiment analysis results")
    parser.add_argument("--review", type=int, help="Generate sentiment analysis and AI review for a specific issue/PR by number")
    args = parser.parse_args()
    
    if args.plot:
        get_plot(args.repo)
    elif args.review is not None:
        get_review_for_item(args.repo, args.review)
    else:
        main(args.repo)
