from langchain.prompts import ChatPromptTemplate
from langchain_core.memory import BaseMemory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough
from app.utils.email_service import send_support_email
from pydantic import BaseModel, Field
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ChatMemory(BaseMemory, BaseModel):
    """自定义对话记忆类"""
    chat_history: List = Field(default_factory=list)
    
    def clear(self):
        self.chat_history = []
    
    @property
    def memory_variables(self) -> List[str]:
        return ["chat_history"]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        formatted_history = ""
        for i in range(0, len(self.chat_history), 2):
            if i + 1 < len(self.chat_history):
                user_msg = self.chat_history[i].content
                ai_msg = self.chat_history[i + 1].content
                formatted_history += f"用户: {user_msg}\n助手: {ai_msg}\n\n"
        return {"chat_history": formatted_history}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        if "input" in inputs and "output" in outputs:
            self.chat_history.append(HumanMessage(content=inputs["input"]))
            self.chat_history.append(AIMessage(content=outputs["output"]))

class CustomerSupportBot:
    def __init__(self):
        """初始化客服机器人"""
        # 初始化聊天模型
        self.chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # 初始化自定义对话记忆
        self.memory = ChatMemory()
        
        # 创建对话提示模板
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的客服助手。请根据用户的问题和对话历史提供帮助。
            
对话历史：
{chat_history}

请记住对话历史，并提供专业、友好的回答。"""),
            ("human", "{input}")
        ])
        
        # 创建对话链
        self.conversation = (
            RunnablePassthrough.assign(
                chat_history=lambda x: self.memory.load_memory_variables({})["chat_history"]
            )
            | self.chat_prompt 
            | self.chat_model
        )
        
        # 创建文档检索提示模板
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的客服助手。请根据提供的上下文信息回答用户的问题。"),
            ("human", "上下文信息:\n{context}\n\n用户问题: {input}")
        ])
        
        # 加载知识库
        self._init_knowledge_base()
        
    def _init_knowledge_base(self):
        """初始化知识库"""
        try:
            # 加载文档
            knowledge_path = os.path.join('app', 'data', 'knowledge_base.txt')
            loader = TextLoader(knowledge_path, encoding='utf-8')
            documents = loader.load()
            
            # 创建向量存储
            embeddings = OpenAIEmbeddings()
            self.vectorstore = FAISS.from_documents(documents, embeddings)
            
            # 创建新的问答链
            combine_docs_chain = create_stuff_documents_chain(
                self.chat_model,
                self.qa_prompt  # 使用包含 context 的提示模板
            )
            
            self.qa_chain = create_retrieval_chain(
                self.vectorstore.as_retriever(),
                combine_docs_chain
            )
            
        except Exception as e:
            logger.error(f"初始化知识库失败: {str(e)}")
            raise
            
    def handle_query(self, user_input: str) -> str:
        """处理用户查询"""
        try:
            # 使用对话链处理输入
            response = self.conversation.invoke({"input": user_input})
            response_text = response.content
            
            # 保存对话到记忆
            self.memory.save_context(
                {"input": user_input},
                {"output": response_text}
            )
            
            # 检查是否需要查询知识库
            if self._needs_knowledge_base(response_text):
                qa_response = self.qa_chain.invoke({
                    "input": user_input,
                    "chat_history": self.memory.load_memory_variables({}).get("chat_history", "")
                })
                if qa_response and hasattr(qa_response, 'answer'):
                    answer = f"根据知识库，您可以参考以下内容：\n{qa_response.answer}"
                    # 保存知识库回答到记忆
                    self.memory.save_context(
                        {"input": user_input},
                        {"output": answer}
                    )
                    return answer
                    
            # 如果无法解决，升级到人工客服
            if self._needs_escalation(response_text):
                return self._escalate_to_human(user_input)
                
            return response_text
            
        except Exception as e:
            logger.error(f"处理查询时出错: {str(e)}")
            return "抱歉，系统出现了一些问题，请稍后再试。"
            
    def _needs_knowledge_base(self, response: str) -> bool:
        """判断是否需要查询知识库"""
        keywords = ['不清楚', '不知道', '无法回答', '需要查询']
        return any(keyword in response for keyword in keywords)
        
    def _needs_escalation(self, response: str) -> bool:
        """判断是否需要升级到人工"""
        keywords = ['无法解决', '需要人工', '太复杂', '建议联系客服']
        return any(keyword in response for keyword in keywords)
        
    def _escalate_to_human(self, query: str) -> str:
        """升级到人工客服"""
        try:
            # 获取完整对话历史
            chat_history = self.memory.load_memory_variables({})["chat_history"]
            
            # 发送邮件通知
            subject = "客服机器人：问题升级通知"
            body = f"""
            收到需要人工处理的问题：
            
            用户问题：{query}
            
            对话历史：
            {chat_history}
            """
            
            send_support_email(subject, body)
            
            return "您的问题可能需要更专业的帮助。我已经将您的问题转交给人工客服，他们会尽快联系您。"
            
        except Exception as e:
            logger.error(f"升级到人工客服失败: {str(e)}")
            return "抱歉，转交人工客服时出现问题。请直接联系我们的客服邮箱：support@example.com" 