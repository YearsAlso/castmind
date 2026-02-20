"""
🎧 API 依赖项

FastAPI 依赖注入
"""

from typing import Optional
from fastapi import Header, HTTPException, Depends
from ..config import CastMindConfig


def get_config() -> CastMindConfig:
    """获取配置依赖"""
    # 这个函数会被覆盖，在 master.py 中设置
    raise NotImplementedError("配置依赖未设置")


def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    config: CastMindConfig = Depends(get_config)
) -> str:
    """
    验证 API Key
    
    Args:
        x_api_key: 请求头中的 API Key
        config: 配置
        
    Returns:
        验证后的 API Key
        
    Raises:
        HTTPException: 如果 API Key 无效
    """
    # 如果未配置 API Key，跳过验证
    if not config.api.api_key:
        return "anonymous"
    
    # 验证 API Key
    if x_api_key != config.api.api_key:
        raise HTTPException(
            status_code=401,
            detail="无效的 API Key"
        )
    
    return x_api_key


def require_admin(
    api_key: str = Depends(verify_api_key),
    config: CastMindConfig = Depends(get_config)
) -> str:
    """
    要求管理员权限
    
    Args:
        api_key: 已验证的 API Key
        config: 配置
        
    Returns:
        管理员 API Key
    """
    # 这里可以添加更复杂的权限检查
    # 例如检查 API Key 是否在管理员列表中
    
    return api_key


def get_pagination_params(
    skip: int = 0,
    limit: int = 100
):
    """
    获取分页参数
    
    Args:
        skip: 跳过数量
        limit: 限制数量
        
    Returns:
        分页参数字典
    """
    # 限制最大数量
    if limit > 1000:
        limit = 1000
    
    return {"skip": skip, "limit": limit}


def get_sort_params(
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """
    获取排序参数
    
    Args:
        sort_by: 排序字段
        sort_order: 排序顺序 (asc/desc)
        
    Returns:
        排序参数字典
    """
    # 验证排序顺序
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"
    
    return {"sort_by": sort_by, "sort_order": sort_order}


def get_filter_params(
    status: Optional[str] = None,
    type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    获取过滤参数
    
    Args:
        status: 状态过滤
        type: 类型过滤
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        过滤参数字典
    """
    filters = {}
    
    if status:
        filters["status"] = status
    if type:
        filters["type"] = type
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    return filters