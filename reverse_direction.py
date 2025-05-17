from neo4j import GraphDatabase

# db connection
uri = "bolt://localhost:7687"
user = "neo4j"
password = "beno@#08"
driver = GraphDatabase.driver(uri, auth=(user, password))

# reverse direction logic
reverse_directions = {
    "east": "west",
    "west": "east",
    "north": "south",
    "south": "north"
}

def create_reverse_directions(tx):
    # Finding all manually created directional relationships
    result = tx.run("""
        MATCH (a)-[r]->(b)
        WHERE r.step_instruction CONTAINS 'Head '
        RETURN a.name AS from_name, b.name AS to_name, r.step_instruction AS instruction
    """)

    for record in result:
        from_node = record["from_name"]
        to_node = record["to_name"]
        instruction = record["instruction"]

        direction = instruction.lower().replace("head ", "").strip()
        reverse_direction = reverse_directions.get(direction)

        if reverse_direction:
            reverse_instruction = f"Head {reverse_direction.capitalize()}"
            check = tx.run("""
                MATCH (b {name: $to_name})-[r]->(a {name: $from_name})
                WHERE r.step_instruction = $reverse_instruction
                RETURN COUNT(r) AS count
            """, from_name=from_node, to_name=to_node, reverse_instruction=reverse_instruction).single()["count"]

            if check == 0: # Create reverse direction relationship
                
                tx.run("""
                    MATCH (a {name: $from_name}), (b {name: $to_name})
                    CREATE (b)-[:PATH {step_instruction: $reverse_instruction}]->(a)
                """, from_name=from_node, to_name=to_node, reverse_instruction=reverse_instruction)

with driver.session() as session:
    session.write_transaction(create_reverse_directions)

driver.close()
