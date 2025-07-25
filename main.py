from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from prompts import context, code_parser_template
from code_reader import code_reader
from dotenv import load_dotenv
import ast
import os

load_dotenv()

llm = Ollama(model="mistral", request_timeout=30.0)

# put document to cloud to parse and get it back to us
parser = LlamaParse(result_type="markdown")
file_extractor = {".pdf": parser}

# load data from data directory
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

# access local model 
embed_model = resolve_embed_model("local:BAAI/bge-m3")
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)


# ask question from pdf
# result = query_engine.query("what are some of the routes in the api?")
# print(result)

tools = [
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="api_documentation",
            description="this gives documentation about code for an API. Use this for reading docs for the API."
        ),
    ),
    code_reader,
]

code_llm = Ollama(model="codellama") # good for code generation
agent = ReActAgent.from_tools(tools, llm=code_llm, verbose=True, context=context)

class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str

parser = PydanticOutputParser(CodeOutput)
json_prompt_str = parser.format(code_parser_template)
json_prompt_template = PromptTemplate(json_prompt_str)

output_pipeline = QueryPipeline(chain=[json_prompt_template, llm])

while (prompt := input("enter a prompt (q to quit): ")) != "q":
    retries = 0

    while retries < 3:
        try:
            result = agent.query(prompt)
            next_result = output_pipeline.run(response=result)
            cleaned_json = ast.literal_eval(str(next_result).replace("assistant:", ""))
            break
        except Exception as e:
            retries += 1
            print("error occured, retry #{retries}: ", e)

    if retries >= 3:
        print("Unable to process request, try again...")
        continue

    print(cleaned_json["code"])
    print("\n\nDescription: ", cleaned_json["description"])

    filename = cleaned_json["filename"]

    try:
        with open(os.path.join("output", filename), "w") as f:
            f.write(cleaned_json["code"])
        print("saved file", filename)
    except:
        print("error saving file...")
    
