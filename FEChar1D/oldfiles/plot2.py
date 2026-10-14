import os


def find_closest_value(file_path, target_value):
    closest_value = None
    corresponding_value = None
    min_difference = float("inf")

    with open(file_path, "r") as file:
        for line in file:
            parts = line.split()
            if len(parts) < 4:
                continue

            try:
                t = float(parts[0])
                temp = float(parts[1])
                pressure = float(parts[2])  # 3rd column
                density = float(parts[3])  # 4th column

                # Change 'pressure' to 'density' if your target value is density
                check_val = pressure

                diff = abs(check_val - target_value)
                if diff < min_difference:
                    min_difference = diff
                    closest_value = check_val
                    corresponding_value = t  # 1st column

            except ValueError:
                continue  # Skip header lines or malformed rows

    return closest_value, corresponding_value


directory = "."  #change to required directory
# Save results2.dat directly inside conv2/
output_path = os.path.join(directory, "interfaceloc.dat")

# Overwrite/clear previous run results
open(output_path, "w").close()

# Check only files matching rho_0.dat to rho_120.dat
for i in range(0, 121):
    filename = f"out_{i}.dat"
    full_path = os.path.join(directory, filename)

    # Skip if file does not exist in the folder
    if not os.path.isfile(full_path):
        continue

    closest_val1, t1 = find_closest_value(full_path, 278.8)
    closest_val2, t2 = find_closest_value(full_path, 221.2)

    print(f"Processed: {filename} -> t1: {t1}, t2: {t2}")

    with open(output_path, "a") as output:
        output.write(f"{i} {t1} {t2}\n")