"""LLM-powered case extraction from raw chat/document text."""
import json
import logging
from openai import OpenAI

from .settings import get_llm_config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个专业的技术案例文档整理专家。你的任务是从聊天记录、排障对话或技术文档中提取关键信息，生成结构化的案例文档。

请严格按照以下 JSON 格式输出，不要添加任何其他内容：

{
  "title": "案例标题（简明扼要，如'群晖ABB虚拟机备份失败排障'）",
  "fault_phenomenon": "故障现象一句话描述",
  "equipment": "涉及的设备/软件及版本",
  "fault_time": "故障发生时间（如有）",
  "personnel": "参与处理的人员（如有）",
  "fault_description": "详细的故障描述，包括错误信息、影响范围",
  "troubleshooting_steps": [
    {
      "step": 1,
      "action": "执行的操作",
      "observation": "观察到的结果",
      "analysis": "分析判断"
    }
  ],
  "root_cause": "问题的根本原因",
  "solution": "最终解决方法，包含具体操作步骤",
  "lessons_learned": [
    "经验教训1",
    "经验教训2"
  ]
}

注意：
1. 保留所有关键参数（IP、版本号、错误码、命令、日志片段）
2. 排查步骤要体现因果逻辑：为什么做这个检查 → 得出什么结论
3. 经验总结要提炼可复用的排查思路
4. 如果某些字段信息不足，写"未提及"而不是编造"""


def get_client() -> OpenAI:
    """Get OpenAI-compatible client."""
    config = get_llm_config()
    return OpenAI(
        api_key=config["api_key"],
        base_url=config["api_base"],
    )


def extract_case(raw_text: str) -> dict:
    """Use LLM to extract structured case info from raw text."""
    config = get_llm_config()
    client = get_client()
    model = config["model"]
    
    logger.info(f"Calling LLM ({model}) to extract case...")
    
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请从以下内容中提取排障案例信息：\n\n{raw_text}"},
        ],
        temperature=0.1,
        max_tokens=4096,
    )
    
    content = resp.choices[0].message.content.strip()
    
    # Try to extract JSON from response (handle markdown code blocks)
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse LLM response as JSON: {content[:200]}")
        return {
            "title": "案例提取失败",
            "fault_phenomenon": "LLM 返回格式异常",
            "equipment": "未提及",
            "fault_time": "未提及",
            "personnel": "未提及",
            "fault_description": content[:500],
            "troubleshooting_steps": [],
            "root_cause": "未提及",
            "solution": "未提及",
            "lessons_learned": [],
        }
