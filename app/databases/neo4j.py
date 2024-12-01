from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    def close(self):
        self.driver.close()
    
    def obtener_eventos_por_periodo(self, fecha_inicio, fecha_fin):
        query = """
        MATCH (e:Evento)
        WHERE toString(e.StartTime) >= $fecha_inicio AND toString(e.StartTime) <= $fecha_fin
        RETURN e.EventId AS EventId, e.LocationLat AS Lat, e.LocationLng AS Lng, 
               e.Severity AS Severity, e.Type AS EventType, toString(e.StartTime) AS StartTime, toString(e.EndTime) AS EndTime
        """
        with self.driver.session() as session:
            return session.run(query, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin).data()
    
    def ejecutar(self, query, parameters):
        with self.driver.session() as session:
            return session.run(query, parameters)
