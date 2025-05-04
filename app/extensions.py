from flask_sqlalchemy import SQLAlchemy
from neo4j import GraphDatabase
from py2neo import Graph





db = SQLAlchemy()


# 在 extensions.py 中添加
neo4j_graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))