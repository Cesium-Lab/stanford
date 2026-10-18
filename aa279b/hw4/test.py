import matlab.engine

# Start MATLAB in the background
eng = matlab.engine.start_matlab()

# Call built-in MATLAB functions
result_sqrt = eng.sqrt(4.0)
print(result_sqrt)  # Outputs: 2.0

# Call functions with multiple return outputs (use nargout)
# Example: gcd(100, 80) returns (gcd, multiplier_1, multiplier_2)
gcd, x, y = eng.gcd(100.0, 80.0, nargout=3)
print(gcd, x, y)  # Outputs: 20.0 1.0 -1.0

# Stop the engine session
eng.quit()