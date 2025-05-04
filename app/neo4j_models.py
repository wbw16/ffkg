from app.extensions import neo4j_graph
from app.models import (
    Basin, River, Reservoir, FloodControlFacility,
    WeatherStation, MonitoringStation
)
from datetime import datetime


class Neo4jSync:
    # 在 sync_all() 方法中添加验证
    @staticmethod
    def sync_all():
        """同步所有数据到 Neo4j"""
        try:
            print("开始数据验证...")
            # 验证各表数据完整性
            if not Neo4jSync.validate_data():
                print("数据验证失败，请检查数据完整性")
                return False

            print("开始同步数据到 Neo4j...")
            Neo4jSync.clear_neo4j_data()
            Neo4jSync.sync_basins()
            Neo4jSync.sync_rivers()
            Neo4jSync.sync_reservoirs()
            Neo4jSync.sync_flood_control_facilities()
            Neo4jSync.sync_weather_stations()
            Neo4jSync.sync_monitoring_stations()
            print("Neo4j 数据同步完成")
            return True
        except Exception as e:
            print(f"同步过程中发生错误: {str(e)}")
            return False

    @staticmethod
    def validate_data():
        """验证数据完整性"""
        try:
            # 验证水库数据
            reservoirs = Reservoir.query.all()
            for res in reservoirs:
                if not all([res.reservoir_id, res.name, res.capacity, res.river_id]):
                    print(f"无效水库记录: ID={res.reservoir_id}, Name={res.name}")
                    return False

            # 可以添加其他表的验证...
            return True
        except Exception as e:
            print(f"数据验证失败: {str(e)}")
            return False

    @staticmethod
    def clear_neo4j_data():
        """清空 Neo4j 现有数据"""
        neo4j_graph.run("MATCH (n) DETACH DELETE n")
        print("已清空 Neo4j 现有数据")

    @staticmethod
    def sync_basins():
        """同步流域数据"""
        basins = Basin.query.all()
        for basin in basins:
            neo4j_graph.run("""
                CREATE (b:Basin {
                    basin_id: $basin_id,
                    name: $name,
                    area: $area,
                    region: $region,
                    created_at: $created_at
                })
            """, parameters={
                'basin_id': basin.basin_id,
                'name': basin.name,
                'area': float(basin.area),
                'region': basin.region,
                'created_at': basin.created_at.isoformat() if basin.created_at else None
            })
        print(f"已同步 {len(basins)} 条流域数据")

    @staticmethod
    def sync_rivers():
        """同步河流数据"""
        rivers = River.query.all()
        for river in rivers:
            neo4j_graph.run("""
                CREATE (r:River {
                    river_id: $river_id,
                    name: $name,
                    length: $length,
                    basin_id: $basin_id,
                    created_at: $created_at
                })
            """, parameters={
                'river_id': river.river_id,
                'name': river.name,
                'length': float(river.length),
                'basin_id': river.basin_id,
                'created_at': river.created_at.isoformat() if river.created_at else None
            })

            # 建立河流与流域的关系
            neo4j_graph.run("""
                MATCH (r:River {river_id: $river_id})
                MATCH (b:Basin {basin_id: $basin_id})
                MERGE (r)-[:BELONGS_TO]->(b)
            """, parameters={
                'river_id': river.river_id,
                'basin_id': river.basin_id
            })
        print(f"已同步 {len(rivers)} 条河流数据")

    @staticmethod
    def sync_reservoirs():
        """同步水库数据"""
        reservoirs = Reservoir.query.all()
        for reservoir in reservoirs:
            # 确保所有必要字段都存在且格式正确
            if not all([reservoir.reservoir_id, reservoir.river_id]):
                print(f"跳过无效水库记录: {reservoir}")
                continue

            params = {
                'reservoir_id': int(reservoir.reservoir_id),
                'name': str(reservoir.name),
                'capacity': float(reservoir.capacity),
                'river_id': int(reservoir.river_id),
                'created_at': reservoir.created_at.isoformat() if reservoir.created_at else None
            }

            try:
                # 创建水库节点
                neo4j_graph.run("""
                       CREATE (res:Reservoir {
                           reservoir_id: $reservoir_id,
                           name: $name,
                           capacity: $capacity,
                           river_id: $river_id,
                           created_at: $created_at
                       })
                   """, parameters=params)

                # 建立水库与河流的关系
                neo4j_graph.run("""
                       MATCH (res:Reservoir {reservoir_id: $reservoir_id})
                       MATCH (r:River {river_id: $river_id})
                       MERGE (res)-[:LOCATED_ON]->(r)
                   """, parameters={
                    'reservoir_id': int(reservoir.reservoir_id),
                    'river_id': int(reservoir.river_id)
                })
            except Exception as e:
                print(f"同步水库 {reservoir.reservoir_id} 失败: {str(e)}")
                continue

        print(f"已同步 {len(reservoirs)} 条水库数据")

    @staticmethod
    def sync_flood_control_facilities():
        """同步防洪设施数据"""
        facilities = FloodControlFacility.query.all()
        for facility in facilities:
            neo4j_graph.run("""
                CREATE (f:FloodControlFacility {
                    facility_id: $facility_id,
                    name: $name,
                    type: $type,
                    river_id: $river_id,
                    created_at: $created_at
                })
            """, parameters={
                'facility_id': facility.facility_id,
                'name': facility.name,
                'type': facility.type,
                'river_id': facility.river_id,
                'created_at': facility.created_at.isoformat() if facility.created_at else None
            })

            # 建立防洪设施与河流的关系
            neo4j_graph.run("""
                MATCH (f:FloodControlFacility {facility_id: $facility_id})
                MATCH (r:River {river_id: $river_id})
                MERGE (f)-[:PROTECTS]->(r)
            """, parameters={
                'facility_id': facility.facility_id,
                'river_id': facility.river_id
            })
        print(f"已同步 {len(facilities)} 条防洪设施数据")

    @staticmethod
    def sync_weather_stations():
        """同步气象站数据"""
        stations = WeatherStation.query.all()
        for station in stations:
            neo4j_graph.run("""
                CREATE (ws:WeatherStation {
                    station_id: $station_id,
                    name: $name,
                    latitude: $latitude,
                    longitude: $longitude,
                    basin_id: $basin_id,
                    created_at: $created_at
                })
            """, parameters={
                'station_id': station.station_id,
                'name': station.name,
                'latitude': float(station.latitude),
                'longitude': float(station.longitude),
                'basin_id': station.basin_id,
                'created_at': station.created_at.isoformat() if station.created_at else None
            })

            # 建立气象站与流域的关系
            neo4j_graph.run("""
                MATCH (ws:WeatherStation {station_id: $station_id})
                MATCH (b:Basin {basin_id: $basin_id})
                MERGE (ws)-[:MONITORS]->(b)
            """, parameters={
                'station_id': station.station_id,
                'basin_id': station.basin_id
            })
        print(f"已同步 {len(stations)} 条气象站数据")

    @staticmethod
    def sync_monitoring_stations():
        """同步监测站数据"""
        stations = MonitoringStation.query.all()
        for station in stations:
            neo4j_graph.run("""
                CREATE (ms:MonitoringStation {
                    monitor_id: $monitor_id,
                    name: $name,
                    type: $type,
                    river_id: $river_id,
                    reservoir_id: $reservoir_id,
                    created_at: $created_at
                })
            """, parameters={
                'monitor_id': station.monitor_id,
                'name': station.name,
                'type': station.type,
                'river_id': station.river_id,
                'reservoir_id': station.reservoir_id,
                'created_at': station.created_at.isoformat() if station.created_at else None
            })

            # 建立监测站与河流或水库的关系
            if station.river_id:
                neo4j_graph.run("""
                    MATCH (ms:MonitoringStation {monitor_id: $monitor_id})
                    MATCH (r:River {river_id: $river_id})
                    MERGE (ms)-[:MONITORS]->(r)
                """, parameters={
                    'monitor_id': station.monitor_id,
                    'river_id': station.river_id
                })

            if station.reservoir_id:
                neo4j_graph.run("""
                    MATCH (ms:MonitoringStation {monitor_id: $monitor_id})
                    MATCH (res:Reservoir {reservoir_id: $reservoir_id})
                    MERGE (ms)-[:MONITORS]->(res)
                """, parameters={
                    'monitor_id': station.monitor_id,
                    'reservoir_id': station.reservoir_id
                })
        print(f"已同步 {len(stations)} 条监测站数据")