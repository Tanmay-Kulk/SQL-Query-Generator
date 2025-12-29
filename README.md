# **PROJECT OVERVIEW**

This project aims to solve a problem that is faced by many professionals. In many enterprises, data is stored in the form of relational databases, but accessing this data requires SQL expertise that many business users might not have prior experience with. Business analysts, product managers, and stakeholders often need quick answers to data questions, but must often write complex queries, which might consume a lot of time. So, in order to reduce time and enable business professionals to focus more on other tasks, I tried to implement this idea, which involves calling OpenAI's API to write the complex queries as an answer to the questions given by the business professionals. In a nutshell, what it does is it allows users to write thoughtful business questions and lets the OpenAI API handle the complex task of generating queries.

# **WHY IT MATTERS?**
This project demonstrates the practical application of AI in solving real business problems. By reducing dependency on technical teams for routine data queries, organizations can focus more on decision-making and empower non-technical stakeholders with self-service analytics. The project also highlights key technical skills, including API integration, database design, prompt engineering, and full-stack deployment—all critical competencies in modern data-driven organizations.

<img width="800" height="800" alt="image" src="https://github.com/user-attachments/assets/f85a7e74-6152-4f85-8f5d-23ee557a71fd" />

Refer to the image above, so instead of writing these types of long queries, we can automate this just by crafting the right questions. 

# **HOW CAN YOU USE THIS REPOSITORY?**
## INSTALLATION & SETUP

In this section, we talk about how you can make the most of this repository. First,  we start by checking if we have all the necessary things needed to kick things off: \
• Python 3.10 or higher \
• OpenAI API key from  this link - _https://platform.openai.com/docs/quickstart_

After getting the API Key, the best practice would be to store it in an Excel file (my approach) or any other way in which it is not publicly exposed. Then, you can clone this repository to get the Python code, which you can use to play around and get familiar with. 

Now, open your command prompt and navigate to your location where you want this repository to be saved. Then type in the following command to clone this repository:

**git clone _link of the repository_**

This will ensure that the files in this repository will be downloaded to your desired location. 

Now, there are many ways in which you can run this code with the API key:

- By directly copying and pasting your API key, this is best when you are experimenting (not recommended when publishing your code publicly).
- By saving it in an Excel file and then further using the pandas library to read that file, and then fetching the key. 
- Lastly, the one I used, since I've deployed this on the Hugging Face platform, there is an option to save _**secret variables**_ so you can do that as well.

After all of this, and successfully running the code, you'll be able to see your app running live on this link shown in the image below. 

<img width="1385" height="130" alt="image" src="https://github.com/user-attachments/assets/5b742cbe-8c5e-4617-9a76-6f4f57a35e93" />

## HUGGING FACE DEPLOYMENT
HuggingFace Spaces is a free platform for hosting machine learning demos, making it ideal for portfolio projects. Start by creating an account at huggingface.co if you don't have one. Navigate to Spaces and click **Create new space**. Give your space a name that you like and this becomes part of the URL. Select Gradio as the SDK and choose Public visibility so anyone can access your application without authentication.

When dealing with API Keys in Hugging face environment, they must be added as a secret variable, not committed to the repository. For that, go to the Settings tab in your Space, then click **Variables and Secrets**. Click **New secret** and create a secret named exactly OPENAI_API_KEY for easier use (note that it is case-sensitive). Paste your OpenAI API key as the value—ensure there are no leading/trailing spaces. 

**IMPORTANT:** Select "Secret" not "Variable"— secrets are encrypted and hidden in logs.

# CONTACT
If you found this repository helpful, feel to connect with me on LinkedIn and I'm happy to take suggestions and feedback that will help me grow! 😄 

**LinkedIn:** _https://www.linkedin.com/in/tanmaykulk/_ 








