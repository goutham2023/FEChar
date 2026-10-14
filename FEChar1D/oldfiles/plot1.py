import numpy as np
import os

# Define the directory containing the rho files
directory = "conv2"  # Assuming the script is in the same directory as the files

# Define the specific locations for interpolation
specific_locations = [0.001, 0.002, 0.004, 0.008, 0.012, 0.016, 0.024]  # for validation2
temp_values = []
dens_values = []
pres_values=[]
time_steps = []

# Iterate through the files
for filename in sorted(os.listdir(directory)):
    if filename.startswith('out_'):
        # Extract the time step from the filename
        time_step = float(filename.split('_')[1].replace('.dat', ''))
        time_steps.append(time_step)

        # Load the data from the file
        data = np.loadtxt(os.path.join(directory, filename))

        # Initialize lists to store interpolated values for this time step
        temp_interp = []
        pres_interp=[]
        dens_interp = []

        # Iterate over each specific location and check if it's within the data range
        for location in specific_locations:
            # Check if location is within the range of the available x data
            if location < data[0, 0] or location > data[-1, 0]:
                # If location is outside of the available data, set the value to 0
                temp_interp.append(0)
                dens_interp.append(0)
                pres_interp.append(0)
            else:
                # Otherwise, interpolate the temperature and density
                temp_interp.append(np.interp(location, data[:, 0], data[:, 1]))
                pres_interp.append(np.interp(location, data[:, 0], data[:, 2]))
                dens_interp.append(np.interp(location, data[:, 0], data[:, 3]))

        # Store the results, adding the time step as the first entry
        temp_values.append(np.concatenate(([time_step], temp_interp)))
        pres_values.append(np.concatenate(([time_step], pres_interp)))
        dens_values.append(np.concatenate(([time_step], dens_interp)))

# Convert lists to numpy arrays for easier manipulation
temp_values = np.array(temp_values)
pres_values = np.array(pres_values)
dens_values = np.array(dens_values)


# Function to sort data and save it to .dat files
def sort_and_save_data(data, output_filename):
    # Sort the data based on the first column (time values)
    sorted_data = data[data[:, 0].argsort()]

    # Save the sorted data to a new .dat file
    np.savetxt(output_filename, sorted_data, fmt='%.3f')

# Save sorted data to .dat files
sort_and_save_data(temp_values, os.path.join(directory, "Indep_temperatures.dat"))
sort_and_save_data(pres_values, os.path.join(directory, "Indep_pressure.dat"))
sort_and_save_data(dens_values, os.path.join(directory, "Indep_density.dat"))

print("done and enjoy")

