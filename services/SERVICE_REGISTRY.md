# EMC知识图谱服务注册表

## 核心服务
| 服务名称          | 路径                  | 功能描述                     |
|-------------------|-----------------------|----------------------------|
| API网关          | `gateway/`            | 统一API入口和路由转发        |
| 知识图谱服务      | `services/knowledge_graph/` | 图数据存储和查询服务         |
| 文件处理服务      | `services/file_processing/` | 文档解析和内容提取           |

## 辅助服务
| 服务名称          | 路径                  | 功能描述                     |
|-------------------|-----------------------|----------------------------|
| AI集成服务        | `services/ai_integration/` | 大模型交互和结果处理         |
| 图编辑服务        | `services/graph_editing/` | 可视化图结构编辑             |
| EMC领域服务       | `services/emc_domain/`    | EMC标准解析和合规检查        |

## 开发指南
```bash
# 启动所有服务
docker-compose up --build

# 单独启动服务
cd services/knowledge_graph
python -m uvicorn main:app --reload
```

## 接口规范
- 所有API使用RESTful设计
- 响应格式: 
```json
{
  "data": {},
  "error": null
}
```
