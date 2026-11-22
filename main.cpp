// This file is distributed under the MIT license.
// See the LICENSE file for details.

/*
  SNOWMAN is currently under active development.
  Features, functionality, and output may change frequently.

  It is created for teaching purposes as part of an HPC (High Performance Computing) course.

  If you encounter any issues feel free to reach out:

  Contact: kmanda@uni-bonn.de
*/

#include <mpi.h>
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include "raytracer.hpp"
#include "scene.hpp"

struct Tile {
    int x, y, w, h;
};

constexpr int WORK_TAG = 1;
constexpr int RESULT_TAG = 2;
constexpr int PIXELS_TAG = 3;

int main(int argc, char* argv[]) {
// Establish a master to slave work distribution here for the MPI. Master divdes to tiles- and gives work to workers. In dynamic manner. Once worker is done - new tile is assigned.
// Workers - update global variable for the main output of tile rendered version.IF this doesnt work we have to build a method for it to be sent to master
// and master then recompiles the final image.(although this can have a lot of overhead and slow down the process)


    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size < 2 || argc < 3) {
        if (rank == 0) {
            std::cout << "Usage: " << argv[0] << " <image_size> <num_snowmen> [tile_size:32]\n";
            std::cout << "Number of MPI processes has to be at least 2\n";
        }
        MPI_Finalize();
        return 1;
    }

    int image_size = std::stoi(argv[1]);
    int num_snowmen = std::stoi(argv[2]);
    int tile_size = (argc > 3) ? std::stoi(argv[3]) : 32;

    // Scene generation and RayTracer setup
    Scene scene;
    scene.generate_snowmen(num_snowmen);

    RayTracer raytracer(image_size, image_size);
    raytracer.set_scene(&scene);

    std::vector<Tile> tiles;
    if (rank == 0) {
        for (int y = 0; y < image_size; y += tile_size) {
            for (int x = 0; x < image_size; x += tile_size) {
                tiles.push_back({
                    x, y,
                    std::min(tile_size, image_size - x),
                    std::min(tile_size, image_size - y)
                });
            }
        }
    }

    std::vector<unsigned char> full_image;
    if (rank == 0) full_image.resize(image_size * image_size * 3);

    auto compute_start_time = std::chrono::high_resolution_clock::now();
        
    if (rank == 0) {
        int tile_index = 0;
        int workers = 0;
        for (int worker = 1; worker < size; worker++) {
            int task[4];
            if (tile_index < tiles.size()) {
                Tile current = tiles[tile_index];
                tile_index++;
                task[0] = current.x;
                task[1] = current.y;
                task[2] = current.w;
                task[3] = current.h;

                MPI_Send(task, 4, MPI_INT, worker, WORK_TAG, MPI_COMM_WORLD);
                workers++;
            } else {
                task[0] = -1;
                MPI_Send(task, 4, MPI_INT, worker, WORK_TAG, MPI_COMM_WORLD);
            }
        }

        while (workers > 0) {
            int result[4];

            MPI_Status status;
            MPI_Recv(result, 4, MPI_INT, MPI_ANY_SOURCE, RESULT_TAG, MPI_COMM_WORLD, &status);

            int worker = status.MPI_SOURCE;
            int x = result[0];
            int y = result[1];
            int w = result[2];
            int h = result[3];

            std::vector<unsigned char> local_pixels(w * h * 3);
            MPI_Recv(local_pixels.data(), local_pixels.size(),
                MPI_UNSIGNED_CHAR, worker, PIXELS_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            for (int row = 0; row < h; ++row) {
                for (int col = 0; col < w; ++col) {
                    int src = (row * w + col) * 3;
                    int dst = ((y + row) * image_size + x + col) * 3;
                    full_image[dst] = local_pixels[src];
                    full_image[dst + 1] = local_pixels[src + 1];
                    full_image[dst + 2] = local_pixels[src + 2];
                }
            }

            if (tile_index < tiles.size()) {
                Tile current = tiles[tile_index];
                tile_index++;
                int task[4] = {current.x, current.y, current.w, current.h};
                MPI_Send(task, 4, MPI_INT, worker, WORK_TAG, MPI_COMM_WORLD);
            } else {
                int task[4] = {-1, 0, 0, 0};
                MPI_Send(task, 4, MPI_INT, worker, WORK_TAG, MPI_COMM_WORLD);
                workers--;
            }
        }
    }
    else {
        raytracer.setup(); // one-time snowflake generation, reused for every tile below
        while (true) {
            int task[4];
            MPI_Status status;
            MPI_Recv(task, 4, MPI_INT, 0, WORK_TAG, MPI_COMM_WORLD, &status);
            if (task[0] == -1) {
                break;
            }
            int x = task[0];
            int y = task[1];
            int w = task[2];
            int h = task[3];
            std::vector<Color> local_pixels;
            // auto render_start_time = std::chrono::high_resolution_clock::now();
            raytracer.render_tile(x, y, w, h, local_pixels);
            // auto render_end_time = std::chrono::high_resolution_clock::now();
            // Convert local_pixels to local_buf for MPI communication
            std::vector<unsigned char> local_buf(local_pixels.size() * 3);
            for (size_t i = 0; i < local_pixels.size(); ++i) {
                local_buf[3*i + 0] = local_pixels[i].r;
                local_buf[3*i + 1] = local_pixels[i].g;
                local_buf[3*i + 2] = local_pixels[i].b;
            }
            int result[4] = {x, y, w, h};
            MPI_Send(result, 4, MPI_INT, 0, RESULT_TAG, MPI_COMM_WORLD);
            MPI_Send(local_buf.data(), local_buf.size(), MPI_UNSIGNED_CHAR, 0, PIXELS_TAG, MPI_COMM_WORLD);
        }
    }

    auto compute_end_time = std::chrono::high_resolution_clock::now();

    // Calculate duration in seconds
    std::chrono::duration<double> local_compute_duration = compute_end_time - compute_start_time;
    double local_compute_time = local_compute_duration.count();

    // Reporting Performance Metrics for Computation
    double max_local_compute_time;
    MPI_Reduce(&local_compute_time, &max_local_compute_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    double min_local_compute_time;
    MPI_Reduce(&local_compute_time, &min_local_compute_time, 1, MPI_DOUBLE, MPI_MIN, 0, MPI_COMM_WORLD);

    double sum_local_compute_time;
    MPI_Reduce(&local_compute_time, &sum_local_compute_time, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        // Image saving
        // Convert full buffer to vector<Color>
        std::vector<Color> full_pixels(image_size * image_size);
        for (int i = 0; i < image_size * image_size; ++i) {
            full_pixels[i] = Color(full_image[3*i], full_image[3*i + 1], full_image[3*i + 2]);
        }

        raytracer.save_image("output.ppm", full_pixels);
        std::cout << "Image saved to output.ppm\n";

        double avg_local_compute_time = sum_local_compute_time / size;

        std::cout << "\n--- Computational Performance Metrics ---\n";
        std::cout << "Image Size: " << image_size << ", Tile Size: " << tile_size << "\n";
        std::cout << "Num Tiles: " << tiles.size() << ", Num Snowmen: " << num_snowmen << ", MPI Processes: " << size << "\n";
        std::cout << "Max Local Computation Time (across all ranks): " << max_local_compute_time << " seconds\n";
        std::cout << "Min Local Computation Time (across all ranks): " << min_local_compute_time << " seconds\n";
        std::cout << "Avg Local Computation Time (across all ranks): " << avg_local_compute_time << " seconds\n";
        std::cout << "Rank 0 / Master Local Computation Time: " << local_compute_time << " seconds\n";
    }

    MPI_Finalize();
    return 0;
}
