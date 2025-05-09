from app.extensions import neo4j_graph
from py2neo import NodeMatcher
from config import Config


def query_knowledge_graph(question):
    """
    查询流域防洪Neo4j知识图谱
    返回格式: {'answer': str, 'entities': list}
    """
    # 初始化节点匹配器
    matcher = NodeMatcher(neo4j_graph)

    # 查询流域信息
    if '流域' in question or 'basin' in question.lower():
        basins = list(matcher.match("Basin").limit(5))
        if basins:
            answer = "以下是一些流域信息:\n" + "\n".join(
                [f"{basin['name']} (面积: {basin['area']}, 地区: {basin['region']})"
                 for basin in basins]
            )
            return {
                'answer': answer,
                'entities': [dict(basin) for basin in basins]
            }

    # 查询河流信息
    elif '河流' in question or 'river' in question.lower():
        rivers = list(neo4j_graph.run(
            "MATCH (r:River)-[:BELONGS_TO]->(b:Basin) "
            "RETURN r, b.name as basin_name LIMIT 5"
        ))
        if rivers:
            answer = "以下是一些河流信息:\n" + "\n".join(
                [f"{record['r']['name']} (长度: {record['r']['length']}), "
                 f"所属流域: {record['basin_name']}"
                 for record in rivers]
            )
            return {
                'answer': answer,
                'entities': [dict(record['r']) for record in rivers]
            }

    # 查询防洪设施
    elif '防洪设施' in question or 'flood control' in question.lower():
        facilities = list(neo4j_graph.run(
            "MATCH (f:FloodControlFacility)-[:PROTECTS]->(r:River) "
            "RETURN f, r.name as river_name LIMIT 5"
        ))
        if facilities:
            answer = "以下是一些防洪设施:\n" + "\n".join(
                [f"{record['f']['name']} (类型: {record['f']['type']}), "
                 f"保护河流: {record['river_name']}"
                 for record in facilities]
            )
            return {
                'answer': answer,
                'entities': [dict(record['f']) for record in facilities]
            }

    # 查询水库信息
    elif '水库' in question or 'reservoir' in question.lower():
        reservoirs = list(neo4j_graph.run(
            "MATCH (res:Reservoir)-[:LOCATED_ON]->(r:River) "
            "RETURN res, r.name as river_name LIMIT 5"
        ))
        if reservoirs:
            answer = "以下是一些水库信息:\n" + "\n".join(
                [f"{record['res']['name']} (容量: {record['res']['capacity']}), "
                 f"所在河流: {record['river_name']}"
                 for record in reservoirs]
            )
            return {
                'answer': answer,
                'entities': [dict(record['res']) for record in reservoirs]
            }

    # 查询监测站信息
    elif '监测站' in question or 'monitoring station' in question.lower():
        stations = list(neo4j_graph.run(
            "MATCH (ms:MonitoringStation) "
            "OPTIONAL MATCH (ms)-[:MONITORS]->(r:River) "
            "OPTIONAL MATCH (ms)-[:MONITORS]->(res:Reservoir) "
            "RETURN ms, r.name as river_name, res.name as reservoir_name "
            "LIMIT 5"
        ))
        if stations:
            answer = "以下是一些监测站信息:\n" + "\n".join(
                [f"{record['ms']['name']} (类型: {record['ms']['type']}), "
                 f"监测目标: {record['river_name'] or record['reservoir_name']}"
                 for record in stations]
            )
            return {
                'answer': answer,
                'entities': [dict(record['ms']) for record in stations]
            }

    # 如果没有匹配的查询类型，返回None
    return None