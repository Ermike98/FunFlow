from funflow import Layer, Model, Template
from typing import Any

# 1. Define custom layers by inheriting from Layer
# We use explicit Template objects even for simple strings to be consistent
class DataLoader(Layer):
    def __init__(self, data_path: str):
        # We define the output name this layer will produce
        super().__init__(name="DataLoader", outputs=[Template("raw_data")])
        self.data_path = data_path

    def call(self) -> list[int]:
        print(f"Loading data from {self.data_path}...")
        return [1, 2, 3, 4, 5]

class DataProcessor(Layer):
    def __init__(self):
        # This layer takes "raw_data" as input and produces "processed_data"
        super().__init__(name="DataProcessor", 
                         inputs=[Template("raw_data")], 
                         outputs=[Template("processed_data")])

    def call(self, raw_data: list[int]) -> list[int]:
        print("Processing data...")
        return [x * 2 for x in raw_data]

class DataSaver(Layer):
    def __init__(self):
        # This layer takes "processed_data" as input
        super().__init__(name="DataSaver", inputs=[Template("processed_data")])

    def call(self, processed_data: list[int]):
        print(f"Saving processed data: {processed_data}")
        # Layer expects a dict-like output if not specified otherwise
        # (Default output_type is 'auto', which handles multiple outputs)
        return {} 

# 2. Instantiate the layers
layers = [
    DataLoader(data_path="data.csv"),
    DataProcessor(),
    DataSaver()
]

# 3. Create the Model
# The model will automatically build the computation graph based on inputs/outputs
model = Model(layers)

# 4. Run the model
if __name__ == "__main__":
    print("--- Running Basic Pipeline ---")
    result = model()
    print("\nFinal State:", result)
