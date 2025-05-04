# app/routes/neo4j_routes.py

from flask import Blueprint, request, jsonify, render_template
from py2neo import Graph, DatabaseError
from app.extensions import neo4j_graph
from flask import request, jsonify
from py2neo import Graph, DatabaseError
import logging
from datetime import datetime
from app.models import River,WeatherStation,Reservoir,FloodControlFacility,Basin,MonitoringStation

neo4j_bp = Blueprint('neo4j', __name__,url_prefix='/neo4j')
logger = logging.getLogger('Neo4jAPI')

@neo4j_bp.route('/')
def index():
    """Neo4j查询首页"""
    return render_template('neo4j/index.html')


@neo4j_bp.route('/basin_river_network/<int:basin_id>')
def get_basin_river_network(basin_id):
    """获取流域-河流网络关系"""
    try:
        query = """
        MATCH (b:Basin {basin_id: $basin_id})<-[:BELONGS_TO]-(r:River)
        OPTIONAL MATCH (r)<-[:LOCATED_ON]-(res:Reservoir)
        OPTIONAL MATCH (r)<-[:PROTECTS]-(f:FloodControlFacility)
        RETURN b, COLLECT(DISTINCT r) AS rivers, 
               COLLECT(DISTINCT res) AS reservoirs,
               COLLECT(DISTINCT f) AS facilities
        """
        result = neo4j_graph.run(query, basin_id=basin_id).data()

        if not result:
            return jsonify({"error": "Basin not found"}), 404

        # 获取SQL数据库中的补充信息
        basin_sql = Basin.query.get(basin_id)
        if not basin_sql:
            return jsonify({"error": "Basin not found in SQL database"}), 404

        return jsonify({
            "basin": dict(result[0]['b']),
            "rivers": [dict(r) for r in result[0]['rivers']],
            "reservoirs": [dict(r) for r in result[0]['reservoirs']],
            "facilities": [dict(f) for f in result[0]['facilities']],
            "sql_data": {
                "basin": {
                    "name": basin_sql.name,
                    "area": basin_sql.area,
                    "region": basin_sql.region,
                    "created_at": basin_sql.created_at.isoformat() if basin_sql.created_at else None
                }
            }
        })
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500


@neo4j_bp.route('/river_full_info/<int:river_id>')
def get_river_full_info(river_id):
    """获取河流完整信息(包含关联实体)"""
    try:
        # Neo4j查询
        query = """
        MATCH (r:River {river_id: $river_id})
        OPTIONAL MATCH (r)-[:BELONGS_TO]->(b:Basin)
        OPTIONAL MATCH (r)<-[:LOCATED_ON]-(res:Reservoir)
        OPTIONAL MATCH (r)<-[:PROTECTS]-(f:FloodControlFacility)
        OPTIONAL MATCH (r)<-[:MONITORS]-(ms:MonitoringStation)
        RETURN r, b, COLLECT(DISTINCT res) AS reservoirs, 
               COLLECT(DISTINCT f) AS facilities,
               COLLECT(DISTINCT ms) AS monitors
        """
        result = neo4j_graph.run(query, river_id=river_id).data()

        if not result:
            return jsonify({"error": "River not found"}), 404

        # SQL数据库查询
        river_sql = River.query.get(river_id)
        if not river_sql:
            return jsonify({"error": "River not found in SQL database"}), 404

        return jsonify({
            "river": dict(result[0]['r']),
            "basin": dict(result[0]['b']) if result[0]['b'] else None,
            "reservoirs": [dict(r) for r in result[0]['reservoirs']],
            "facilities": [dict(f) for f in result[0]['facilities']],
            "monitors": [dict(m) for m in result[0]['monitors']],
            "sql_data": {
                "river": {
                    "name": river_sql.name,
                    "length": river_sql.length,
                    "created_at": river_sql.created_at.isoformat() if river_sql.created_at else None
                },
                "basin": {
                    "name": river_sql.basin.name if river_sql.basin else None
                }
            }
        })
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500


@neo4j_bp.route('/monitoring_network/<int:basin_id>')
def get_monitoring_network(basin_id):
    """获取流域监测网络(气象站+监测站)"""
    try:
        query = """
        MATCH (b:Basin {basin_id: $basin_id})
        OPTIONAL MATCH (b)<-[:MONITORS]-(ws:WeatherStation)
        OPTIONAL MATCH (ws)-[:MONITORS]->(b)
        OPTIONAL MATCH (ms:MonitoringStation)-[:MONITORS]->(r:River)-[:BELONGS_TO]->(b)
        RETURN b, COLLECT(DISTINCT ws) AS weather_stations, 
               COLLECT(DISTINCT ms) AS monitoring_stations
        """
        result = neo4j_graph.run(query, basin_id=basin_id).data()

        if not result:
            return jsonify({"error": "Basin not found"}), 404

        # SQL数据库查询
        basin_sql = Basin.query.get(basin_id)
        if not basin_sql:
            return jsonify({"error": "Basin not found in SQL database"}), 404

        return jsonify({
            "basin": dict(result[0]['b']),
            "weather_stations": [dict(ws) for ws in result[0]['weather_stations']],
            "monitoring_stations": [dict(ms) for ms in result[0]['monitoring_stations']],
            "sql_data": {
                "basin": {
                    "name": basin_sql.name,
                    "area": basin_sql.area,
                    "region": basin_sql.region
                }
            }
        })
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500


@neo4j_bp.route('/flood_control_system/<int:river_id>')
def get_flood_control_system(river_id):
    """获取河流防洪系统(防洪设施+水库)"""
    try:
        query = """
        MATCH (r:River {river_id: $river_id})
        OPTIONAL MATCH (r)<-[:PROTECTS]-(f:FloodControlFacility)
        OPTIONAL MATCH (res:Reservoir)-[:LOCATED_ON]->(r)
        RETURN r, COLLECT(DISTINCT f) AS facilities, 
               COLLECT(DISTINCT res) AS reservoirs
        """
        result = neo4j_graph.run(query, river_id=river_id).data()

        if not result:
            return jsonify({"error": "River not found"}), 404

        # SQL数据库查询
        river_sql = River.query.get(river_id)
        if not river_sql:
            return jsonify({"error": "River not found in SQL database"}), 404

        return jsonify({
            "river": dict(result[0]['r']),
            "facilities": [dict(f) for f in result[0]['facilities']],
            "reservoirs": [dict(r) for r in result[0]['reservoirs']],
            "sql_data": {
                "river": {
                    "name": river_sql.name,
                    "length": river_sql.length
                },
                "flood_alerts": [{
                    "alert_level": alert.alert_level,
                    "timestamp": alert.timestamp.isoformat(),
                    "description": alert.description
                } for alert in river_sql.flood_alerts.limit(5).all()]
            }
        })
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500


@neo4j_bp.route('/search_entities', methods=['GET'])
def search_entities():
    """搜索实体(跨类型搜索)"""
    search_term = request.args.get('q', '').strip()
    if not search_term:
        return jsonify({"error": "Search term is required"}), 400

    try:
        # 使用正则表达式进行模糊查询
        query = """
        MATCH (n)
        WHERE (n:Basin OR n:River OR n:Reservoir OR n:FloodControlFacility OR n:WeatherStation OR n:MonitoringStation)
          AND toLower(n.name) CONTAINS toLower($search_term)
        RETURN labels(n)[0] AS type, properties(n) AS properties
        LIMIT 20
        """
        results = neo4j_graph.run(query, search_term=search_term).data()

        # 对每个结果添加SQL补充信息
        enriched_results = []
        for result in results:
            entity_type = result['type']
            properties = result['properties']
            enriched = {
                "type": entity_type,
                "properties": properties,
                "score": 1.0  # 简单匹配，分数设为1
            }

            # 根据类型获取SQL补充数据
            if entity_type == "Basin":
                sql_obj = Basin.query.get(properties['basin_id'])
            elif entity_type == "River":
                sql_obj = River.query.get(properties['river_id'])
            elif entity_type == "Reservoir":
                sql_obj = Reservoir.query.get(properties['reservoir_id'])
            elif entity_type == "FloodControlFacility":
                sql_obj = FloodControlFacility.query.get(properties['facility_id'])
            elif entity_type == "WeatherStation":
                sql_obj = WeatherStation.query.get(properties['station_id'])
            elif entity_type == "MonitoringStation":
                sql_obj = MonitoringStation.query.get(properties['monitor_id'])
            else:
                sql_obj = None

            if sql_obj:
                enriched["sql_data"] = {
                    "created_at": sql_obj.created_at.isoformat() if hasattr(sql_obj, 'created_at') else None,
                    "name": sql_obj.name if hasattr(sql_obj, 'name') else None
                }

            enriched_results.append(enriched)

        logger.info(f"Search results for '{search_term}': {len(enriched_results)} items found")
        return jsonify({"results": enriched_results})

    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('neo4j_api.log'),  # 日志文件
        logging.StreamHandler()  # 控制台输出
    ]
)


@neo4j_bp.route('/query', methods=['POST'])
def neo4j_query():
    """
    Neo4j 查询转发接口
    返回原生 Neo4j JSON 格式数据（包含元数据）
    """
    request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    logger.info(f"[{request_id}] 收到新请求 | 方法: {request.method} | IP: {request.remote_addr}")

    try:
        # 解析请求数据
        data = request.get_json()
        logger.debug(f"[{request_id}] 请求数据: {data}")

        if not data or 'query' not in data:
            logger.error(f"[{request_id}] 缺少必要参数: query")
            return jsonify({"error": "Missing query parameter"}), 400

        query = data['query']
        parameters = data.get('parameters', {})

        # 记录查询信息（隐藏敏感参数）
        safe_params = {k: '*****' if 'password' in k.lower() else v
                      for k, v in parameters.items()}
        logger.info(f"[{request_id}] 执行查询 | 查询: {query[:100]}... | 参数: {safe_params}")

        # 执行查询并获取原生结果
        start_time = datetime.now()
        result = list(neo4j_graph.run(query, parameters))  # 获取原始记录对象列表
        exec_time = (datetime.now() - start_time).total_seconds()

        # 转换为原生 Neo4j JSON 格式
        neo4j_native_result = []
        for record in result:
            neo4j_native_result.append({
                "keys": list(record.keys()),
                "length": len(record),
                "_fields": [dict(field.items()) if hasattr(field, 'items') else field
                           for field in record.values()],
                "_fieldLookup": {key: idx for idx, key in enumerate(record.keys())}
            })

        result_size = len(neo4j_native_result)
        logger.info(
            f"[{request_id}] 查询成功 | 耗时: {exec_time:.3f}s | 返回结果数: {result_size}"
        )
        logger.debug(f"[{request_id}] 示例结果: {str(neo4j_native_result[:1])[:200]}...")
        logger.info(f"[{request_id}] 查询结果: {neo4j_native_result}")
        return jsonify({
            "success": True,
            "data": neo4j_native_result,  # 返回原生格式
            "metadata": {
                "request_id": request_id,
                "execution_time": exec_time,
                "result_count": result_size
            }
        })

    except DatabaseError as e:
        logger.error(f"[{request_id}] Neo4j数据库错误: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "request_id": request_id,
            "type": "database_error"
        }), 400

    except Exception as e:
        logger.error(f"[{request_id}] 服务器内部错误: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "request_id": request_id,
            "type": "internal_error"
        }), 500

    finally:
        logger.info(f"[{request_id}] 请求处理完成")
# @neo4j_bp.route('/query', methods=['POST'])
# def neo4j_query():
#     """
#     Neo4j 查询转发接口
#     接收 JSON 格式请求: {"query": "CYPHER_QUERY", "parameters": {}}
#     """
#     # 记录请求开始
#     request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
#     logger.info(f"[{request_id}] 收到新请求 | 方法: {request.method} | IP: {request.remote_addr}")
#
#     try:
#         # 解析请求数据
#         data = request.get_json()
#         logger.debug(f"[{request_id}] 请求数据: {data}")
#
#         if not data or 'query' not in data:
#             logger.error(f"[{request_id}] 缺少必要参数: query")
#             return jsonify({"error": "Missing query parameter"}), 400
#
#         query = data['query']
#         parameters = data.get('parameters', {})
#
#         # 记录查询信息（隐藏敏感参数）
#         safe_params = {k: '*****' if 'password' in k.lower() else v
#                        for k, v in parameters.items()}
#         logger.info(f"[{request_id}] 执行查询 | 查询: {query[:100]}... | 参数: {safe_params}")
#
#         # 执行查询
#         start_time = datetime.now()
#         result = neo4j_graph.run(query, parameters).data()
#         exec_time = (datetime.now() - start_time).total_seconds()
#
#         # 记录查询结果
#         result_size = len(result)
#         logger.info(
#             f"[{request_id}] 查询成功 | 耗时: {exec_time:.3f}s | 返回结果数: {result_size}"
#         )
#         logger.debug(f"[{request_id}] 示例结果: {str(result[:1])[:200]}...")
#         logger.info(f"[{request_id}] 查询结果: {result}")
#         return jsonify({
#             "success": True,
#             "data": result,
#             "metadata": {
#                 "request_id": request_id,
#                 "execution_time": exec_time,
#                 "result_count": result_size
#             }
#         })
#
#     except DatabaseError as e:
#         logger.error(f"[{request_id}] Neo4j数据库错误: {str(e)}", exc_info=True)
#         return jsonify({
#             "error": str(e),
#             "request_id": request_id,
#             "type": "database_error"
#         }), 400
#
#     except Exception as e:
#         logger.error(f"[{request_id}] 服务器内部错误: {str(e)}", exc_info=True)
#         return jsonify({
#             "error": f"Internal server error: {str(e)}",
#             "request_id": request_id,
#             "type": "internal_error"
#         }), 500
#
#     finally:
#         # 确保每个请求都有结束标记
#         logger.info(f"[{request_id}] 请求处理完成")

@neo4j_bp.route('/health')
def health_check():
    try:
        # 测试Neo4j连接
        result = neo4j_graph.run("RETURN 1").data()
        return jsonify({"status": "healthy", "neo4j": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500