# Streamlit App Deployment to AWS S3

This project demonstrates how to deploy a Streamlit application to AWS S3 using GitHub Actions. The app is exported to static files and hosted on S3 for easy access and scalability.

## Features

- **Streamlit Application**: A Python-based web application built with Streamlit.
- **AWS S3 Hosting**: Static files are hosted on AWS S3 for reliable and scalable access.
- **CI/CD with GitHub Actions**: Automated deployment pipeline using GitHub Actions.

## Prerequisites

- **AWS Account**: An AWS account with access to S3 and Secrets Manager.
- **GitHub Account**: A GitHub account to host the repository and manage actions.
- **Python 3.8+**: Ensure Python is installed on your local machine.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS**:
   - Create an S3 bucket for hosting the static files.
   - Store your LangSmith API key in AWS Secrets Manager.

4. **Set Up GitHub Secrets**:
   - Go to your GitHub repository settings.
   - Add the following secrets:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `AWS_REGION`
     - `S3_BUCKET_NAME`

## Deployment

1. **Push Changes**:
   - Ensure your changes are committed to the `main` branch.
   - Push to GitHub to trigger the deployment workflow.

2. **GitHub Actions**:
   - The workflow defined in `.github/workflows/deploy.yml` will automatically build and deploy your app to S3.

## Usage

- Access your deployed Streamlit app via the S3 bucket URL.
- Optionally, configure a custom domain using AWS Route 53 for a user-friendly URL.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com).
