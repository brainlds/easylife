import logging
from .llm_clients import create_llm_client
from .test_helper import get_test_questions  # 导入测试生成函数

# 配置日志
logger = logging.getLogger(__name__)

def get_chat_response(question, provider="openai"):
    """
    获取AI回答
    
    @param question: 用户问题
    @param provider: 模型提供商
    @return: AI回答
    """
    try:
        # 创建LLM客户端
        client = create_llm_client(provider)
        
        # 构建消息
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
        
        # 获取回答
        response = client.get_completion(messages)
        logger.debug(f"{provider} 响应: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"调用 {provider} 失败: {str(e)}")
        raise

# 导出测试生成函数
__all__ = ['get_chat_response', 'get_test_questions'] 