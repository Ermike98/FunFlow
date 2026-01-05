from funflow import GridMap, Model, Template, Tag, NoTagFilter, ValueTagFilter

# 1. Advanced Routing with GridMap
# GridMap is the primary way to perform selective routing and 
# cross-product joins of tagged data in FunFlow.

# 2. Define Advanced Layers

# SensorFilter: Processes only 'type:sensor' data
sensor_filter = GridMap(
    lambda x: x * 1.5,
    inputs=[Template("data", filters=[ValueTagFilter("type", "sensor"), NoTagFilter("id")])],
    outputs=[Template("sensor_processed", filters=[NoTagFilter("id")])],
    name="SensorFilter"
)

# CombinedProcessor: Joins 'sensor_processed' and 'log_data' on the SAME 'id' tag.
# GridMap will only execute this for combinations where 'id' matches and exists in both.
combined_processor = GridMap(
    lambda s, l: s + l,
    inputs=[
        Template("sensor_processed", filters=[NoTagFilter("id")]),
        Template("log_data", filters=[NoTagFilter("id")])
    ],
    outputs=[Template("final_summary", filters=[NoTagFilter("id")])],
    name="CombinedProcessor"
)

# 3. Create the Model
model = Model([sensor_filter, combined_processor])

# 4. Run the model
if __name__ == "__main__":
    print("--- Running Complex Routing Example with GridMap ---")
    
    inputs = {
        "data, type:sensor, id:1": 10,
        "data, type:sensor, id:2": 20,
        "data, type:manual, id:3": 50, # Ignored by SensorFilter
        "log_data, id:1": 5,
        "log_data, id:2": 8
    }
    
    result = model(**inputs)
    
    print("\nResults Produced:")
    for k, v in result.items():
        if any(x in k for x in ["sensor_processed", "final_summary"]):
            print(f"  {k} = {v}")

    # Expected:
    # sensor_processed, id:1 = 15.0
    # sensor_processed, id:2 = 30.0
    # final_summary, id:1 = 20.0
    # final_summary, id:2 = 38.0
