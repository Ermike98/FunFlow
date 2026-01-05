from funflow import Functional, Model, Template
import math

# 1. Define nodes using the Functional layer
# We use explicit Template objects to ensure consistency.

layers = [
    # A simple lambda function
    Functional(lambda x: x**2, 
               inputs=[Template("base_value")], 
               outputs=[Template("squared_value")]),
    
    # Another lambda for branching (it will take the same 'base_value')
    Functional(lambda x: math.sqrt(x), 
               inputs=[Template("base_value")], 
               outputs=[Template("sqrt_value")]),
    
    # A regular function for merging multiple inputs
    Functional(
        lambda a, b: a + b, 
        inputs=[Template("squared_value"), Template("sqrt_value")], 
        outputs=[Template("combined_result")],
        name="SumNode"
    ),
    
    # Node with multiple outputs
    # When a function returns a tuple/list, the outputs are mapped in order
    Functional(
        lambda x: (x + 1, x + 2),
        inputs=[Template("combined_result")],
        outputs=[Template("final_plus_1"), Template("final_plus_2")],
        name="MultiOutputNode"
    )
]

# 2. Create the Model
model = Model(layers)

# 3. Run the model with initial input
if __name__ == "__main__":
    print("--- Running Functional Nodes Pipeline ---")
    result = model(base_value=16)

    # 4. Display results
    print("\nInputs: base_value=16")
    print(f"16^2 = {result['squared_value']}")
    print(f"sqrt(16) = {result['sqrt_value']}")
    print(f"Sum = {result['combined_result']}")
    print(f"Final Results: {result['final_plus_1']}, {result['final_plus_2']}")
