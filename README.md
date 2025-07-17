# core_pyhton_llm
https://www.youtube.com/watch?v=JLmI0GJuGlY

Things used:
- LlamaIndex
- Ollama
- Multi-LLM

Things learned:
- Agents and Projects
- Llama Parse
- Tools and creating custom tools
- Output parser and second LLM
- Retry handle
- Saving to a file

Flow:
- Put a document to cloud and get it back to us using LlamaParse (it is to efficiently parse pdf to ensure good quality)
- Load the local data and put it to the file parser
- Use mistral model that is good for general purpose task and use the local model
- Define the tools, we can use the one available or make a custom one
- Create other model that is good for code generation
- Use react agent so that it can decide which tool to use
- Format the output to json using PydanticOutputParser
- Write it to a file
