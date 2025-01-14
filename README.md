## AI Copilot to help in personal tasks

#### Prerequisites
- Setup [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)
- Retrieve [Calendly AUTH Token & User URI](https://developer.calendly.com/api-docs/be9b32ef4b44c-get-access-token)
- Get [GNews API Key](https://gnews.io/docs/v4#authentication)
- Add above keys in `.env` in the following format

```
# filename: .env
CALENDLY_AUTH_TOKEN=<AUTH_TOKEN>
CALENDLY_USER_URI=<USER_URI>
GNEWS_API_KEY=<API_KEY>
```

### Verify AWS authentication
```
aws sts get-caller-identity
```
If successful, this command will return your AWS account ID, user ID, and ARN.


### Run
- Install [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
```
conda create -p venv python=3.12
conda activate ./venv
pip install -r requirements.txt

chainlit run app.py --port 8888
```
### Agents
This personal assistant uses [AWS Multi-Agent Orchestrator](https://github.com/awslabs/multi-agent-orchestrator) for managing the agents. It contains following agents

#### Calendar Agent
- This agent utilizes Calendly APIs to retrieve meeting invitations to provide a summary of calendar events for the next 10 days. 

#### News Reader Agent
- This agent utilizes `gnews.io` APIs to retrieve news and summarizes the news. 

#### Fitness Agent
- This standalone agent specializes in recommendations on fitness routines, diet plans and general health tips

