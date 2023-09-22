import numpy as np
from sklearn.neighbors import KDTree
def assign_data_to_particles(particles, new_data):
    m, n = particles.shape
    k, _ = new_data.shape

    if n != new_data.shape[1]:
        raise ValueError("Number of columns in particles and new_data must match.")

    # Build a KD tree from the particles
    kdtree = KDTree(particles, metric='manhattan')

    # Calculate the sum of particle elements along columns
    sum_particles = np.sum(particles, axis=1)

    # Calculate the threshold for similarity based on 10% of sum_particles + 2
    threshold = 0.15 * sum_particles + 2

    # Query the KD tree to find the closest particles for each new data point
    distances, closest_particle_indices = kdtree.query(new_data, k=1)

    # Initialize the labels array
    labels = np.zeros(k, dtype=int)

    for i in range(k):
        if distances[i] > threshold[closest_particle_indices[i]]:  # Use the threshold corresponding to each new data point
            labels[i] = -999  # If the distance is greater than the threshold, mark as unassigned
        else:
            labels[i] = closest_particle_indices[i]  # Assign the label as the closest particle index

    return labels
