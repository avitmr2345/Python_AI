from langchain_community.tools import DuckDuckGoSearchRun, ShellTool
from langchain_core.tools import tool
from langchain.tools import StructuredTool, BaseTool
from pydantic import BaseModel, Field
from typing import Type


# 1. Built in tools
search_tool = DuckDuckGoSearchRun()
shell_tool = ShellTool()

result1 = search_tool.invoke('top news in india today')
result2 = shell_tool.invoke('ls')

print(result1)
print(result2)
print(search_tool.name)
print(search_tool.description)
print(search_tool.args)

# 2. Custom tools

# Step 1 - create a function
def multiply(a, b):
    """Multiply two numbers"""
    return a*b

# Step 2 - add type hints
def multiply(a: int, b:int) -> int:
    """Multiply two numbers"""
    return a*b

# Step 3 - add tool decorator
@tool
def multiply(a: int, b:int) -> int:
    """Multiply two numbers"""
    return a*b

result = multiply.invoke({"a":3, "b":5})
print(result)
print(multiply.args_schema.model_json_schema())

# 3. Structured tools
class MultiplyInput(BaseModel):
    a: int = Field(required=True, description="The first number to add")
    b: int = Field(required=True, description="The second number to add")

def multiply_func(a: int, b: int) -> int:
    return a * b

multiply_tool = StructuredTool.from_function(
    func=multiply_func,
    name="multiply",
    description="Multiply two numbers",
    args_schema=MultiplyInput
)

result = multiply_tool.invoke({'a':3, 'b':3})

print(result)
print(multiply_tool.name)
print(multiply_tool.description)
print(multiply_tool.args)

# 4. Structured tools using BaseTool

# arg schema using pydantic
class MultiplyInput(BaseModel):
    a: int = Field(required=True, description="The first number to add")
    b: int = Field(required=True, description="The second number to add")

class MultiplyTool(BaseTool):
    name: str = "multiply"
    description: str = "Multiply two numbers"

    args_schema: Type[BaseModel] = MultiplyInput

    def _run(self, a: int, b: int) -> int:
        return a * b

multiply_tool = MultiplyTool()

result = multiply_tool.invoke({'a':3, 'b':3})

print(result)
print(multiply_tool.name)
print(multiply_tool.description)
print(multiply_tool.args)

# 5. Toolkit

# Custom tools
@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

class MathToolkit:
    def get_tools(self):
        return [add, multiply]

toolkit = MathToolkit()
tools = toolkit.get_tools()

for tool in tools:
    print(tool.name, "=>", tool.description)
