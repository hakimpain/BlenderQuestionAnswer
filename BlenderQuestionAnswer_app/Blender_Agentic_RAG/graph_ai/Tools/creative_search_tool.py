
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models.base import BaseChatModel
from langchain_core.documents import Document

class CreativeTool(BaseTool):

    llm_creative: BaseChatModel
    version: str

    name:str = 'creative_tool'
    description:str = (
        'Look for creative solutions or ideas for a Blender project or task\n'
        'Args:\n'
        'query: question related to a Blender 3D project or task'
        )

    def _run(self,query:str):
        prompt_str = ("Answer creative solutions or ideas related to a Blender 3D software projec for the question:\n{question}\n"
        f"If possible answer based on the blender {self.version} version.")
        prompt = PromptTemplate(template=prompt_str,input_variables=['question'])
        chain = prompt | self.llm_creative | StrOutputParser()
        response = chain.invoke({'question':query})
        return [Document(page_content=response)]