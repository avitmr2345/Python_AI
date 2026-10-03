from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI()

# detailed way
template = PromptTemplate(
    template='Greet this person in 3 languages. The name of the person is {name}',
    input_variables=['name']
)

# saving the prompt template to a file and use with load_prompt
# template.save('prompt_template.json')

# fill the values of the placeholders
prompt = template.invoke({'name':'avish'})

result = model.invoke(prompt)

# invoking the model with a single static prompt
# result = model.invoke("What is the capital of France?")

print(result.content)
