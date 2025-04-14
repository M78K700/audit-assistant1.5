# Financial Audit Assistant

A Streamlit application that helps generate comprehensive audit plans based on company information and sector-specific requirements.

## Features

- Dynamic audit team management
- Sector-specific audit planning
- Compliance with IFRS and US GAAP
- Professional PDF report generation
- Audit history tracking

## Local Development

1. Clone the repository
2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

## Deployment to Streamlit Cloud

1. Create a GitHub repository and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your_repository_url
   git push -u origin main
   ```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and main file path (app.py)
6. Add your OpenAI API key in the Streamlit Cloud secrets management:
   - Go to your app settings
   - Click on "Secrets"
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
7. Deploy your app

## Security Notes

- Never commit your `.env` file or expose your API keys
- Use Streamlit Cloud's secrets management for sensitive information
- Keep your dependencies updated for security patches

## License

MIT License 