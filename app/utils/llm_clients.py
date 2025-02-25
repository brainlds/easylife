from abc import ABC, abstractmethod
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import List, Any, Optional, Dict
from pydantic import BaseModel, Field  # 使用 pydantic v2

# 配置日志
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    @abstractmethod
    def get_completion(self, messages):
        """获取模型回复"""
        pass

class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1"
        )
        
    def get_completion(self, messages):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        # 打印响应
        logger.info(f"\nOpenAI响应:\n{response.choices[0].message.content}\n")
        return response.choices[0].message.content

class DeepSeekClient(BaseChatModel, BaseModel):
    """DeepSeek API 客户端"""
    
    name: str = "deepseek_chat"
    description: str = "DeepSeek Chat API"
    
    client: Any = Field(default=None)
    dashscope_client: Any = Field(default=None)  # 添加通义千问客户端
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化 DeepSeek 客户端
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            # base_url="https://api.deepseek.com/v1",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        # 初始化通义千问客户端作为备用
        self.dashscope_client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    def get_completion(self, messages):
        response = self.client.chat.completions.create(
            model="deepseek-r1",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        # 打印响应
        logger.info(f"\nOpenAI响应:\n{response.choices[0].message.content}\n")
        return response.choices[0].message.content
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成回复"""
        # 将消息转换为 OpenAI 格式
        formatted_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted_messages.append({"role": "assistant", "content": message.content})
            else:
                formatted_messages.append({"role": "system", "content": message.content})
        
        # 记录请求信息
        logger.debug(f"请求消息: {formatted_messages}")
        
        # 首先尝试使用 DeepSeek
        try:
            response = self.client.chat.completions.create(
                # model="deepseek-chat",
                model="deepseek-r1",
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=8000,
                stop=stop
            )
            
            content = response.choices[0].message.content
            logger.info(f"\nDeepSeek响应成功:\n{content}\n")
            
            return ChatResult(generations=[
                ChatGeneration(message=AIMessage(content=content))
            ])
            
        except Exception as deepseek_error:
            logger.warning(f"DeepSeek调用失败，切换到通义千问: {str(deepseek_error)}")
            
            try:
                # 使用通义千问作为备用
                response = self.dashscope_client.chat.completions.create(
                    model="qwen-turbo",
                    messages=formatted_messages,
                    temperature=0.7,
                    max_tokens=4000,
                    stop=stop
                )
                
                content = response.choices[0].message.content
                logger.info(f"\n通义千问响应成功:\n{content}\n")
                
                return ChatResult(generations=[
                    ChatGeneration(message=AIMessage(content=content))
                ])
                
            except Exception as qwen_error:
                logger.error(f"通义千问也失败了: {str(qwen_error)}")
                logger.error("详细错误信息: ", exc_info=True)
                
                # 返回一个友好的错误消息
                error_message = "很抱歉，生成旅行计划时遇到了问题。请稍后重试。"
                return ChatResult(generations=[
                    ChatGeneration(message=AIMessage(content=error_message))
                ])
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": "deepseek-chat"}

class DashScopeClient(BaseLLMClient):
    """DashScope API客户端"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
    def get_completion(self, messages):
        completion = self.client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=messages,
            modalities=["text"],
            stream=True
        )
        
        full_response = ""
        for chunk in completion:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    logger.debug(f"收到响应片段: {content}")
        
        # 打印完整响应
        logger.info(f"\nDashScope响应:\n{full_response}\n")
        return full_response

def create_llm_client(provider="openai"):
    """
    LLM客户端工厂函数
    
    @param provider: 模型提供商，可选值：openai, deepseek, dashscope
    @return: LLM客户端实例
    """
    clients = {
        "openai": OpenAIClient,
        "deepseek": DeepSeekClient,
        "dashscope": DashScopeClient
    }
    
    client_class = clients.get(provider.lower())
    if not client_class:
        raise ValueError(f"不支持的模型提供商: {provider}")
        
    return client_class() 