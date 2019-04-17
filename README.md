Last update: April 17, 2019 13:00

***** This readme file will be used as 'project status' unitl the code is complete and robust *****

# lazor_solver
module to solve for board puzzles of the "Lazors" game in Android and iOS


## Changes in `dev` branch

- refactor `solve.py` and other module files inside `pylazors`.
- add a `_solver.py` which contains functions used to solve large boards.
- add a wrapper function in `solve.py`, `solve_board()`. This function will check the size of the given board, 
  if it is small, use `_solve_board()` in `solve.py`, and if it is large, use `_solve_large_board()` in `_solve.py`.
- add a small main script `lazors.py`
- add error handling

## Todos
- (maybe?) more Error handing and Unit testing
- Add back docstrings in original main script (project description, file information, etc)
- the function *get_possible_combs_perm* returns more than needed combinations, this can be due to sorting issues
- possibly after commiting the image loader, merge with the bff_loader to take input as either bff file or image


## Requirements

- Python 3.6 or higher
- `numpy` and `Pillow`


## Tested environment
- Python 3.7.3 with `numpy (v1.15.2)` and `Pillow (v5.4.1)`


## Usage

You can use this project by running the batch script directly, or import `pylazors` as a module in your own codes.

### Using batch script `lazors.py`

You can solve all board files given in the handout by running:
```bash
$ python3 lazors.py
```

When running, the script `lazors.py` will create a `solutions` folder, import and solve all `.BFF` inside 
`boards/handout`, and write solutions as `.PNG` files in `solutions` folder.

You can uncomment the last line in `lazors.py` to also solve all boards in `boards/all` in parallel as well.

### Using `pylazors` module

The `pylazors` contains classes and functions that can be used to read and write a board, and solve a board. Here is a simple example:
```python
import pylazors

# Import .BFF file as a <pylazors.Board> object
board = pylazors.read_bff('boards/handout/dark_1.bff')

# Solve board
solution = pylazors.solve_board(board)

# Write solution as an image
pylazors.write_png(solution, 'solutions/dark_1.png')
```

## Underdevelopment

  - Image loader of board to solve
    the initial image processessing can yield the following, wondering if Template Matching can work here?

  <img src="/utilites/img_reader/Mad_7.jpg" alt="drawing" width="200"/> ---> <img src="/utilites/img_reader/Result_IMAGE.png" alt="drawing" width="200"/>


  <img src="/utilites/img_reader/Diagonal_3.jpg" alt="drawing" width="200"/> ---> <img src="/utilites/img_reader/Result_IMAGE_Diagonal_3.png" alt="drawing" width="200"/>


## Performance

Following performance benchmarks were obtained using a quad-core 2.6 GHz processor.

#### Serial

- for 8 boards in `boards/handout`:

    ```
	total wall time: 12.10 seconds. 
	total CPU time:  10.955 seconds (min/avg/max 0.002/1.369/5.779). 
	5 slowest boards: yarn_5 (5.8s), mad_7 (4.5s), showstopper_4 (0.2s), numbered_6 (0.2s), mad_4 (0.1s)
    ```

- for 157 boards in `boards/all`:

    ```
	total wall time: 715.65 seconds. 
	total CPU time:  692.290 seconds (min/avg/max 0.000/4.409/226.741). 
	5 slowest boards: showstopper_9 (226.7s), grande_10 (132.5s), diagonal_10 (115.9s), showstopper_10 (59.5s), grande_9 (18.2s)
    ```

#### Parallel (using 4 processes)

- for 8 boards in `boards/handout`:

    ```
	total wall time: 6.19 seconds.
	total CPU time:  11.375 seconds (min/avg/max 0.001/1.422/5.971).
	5 slowest boards: yarn_5 (6.0s), mad_7 (4.6s), numbered_6 (0.3s), showstopper_4 (0.2s), mad_4 (0.2s)
    ```

- for 157 boards in `boards/all`:

    ```
	total wall time: 283.41 seconds.
	total CPU time:  898.729 seconds (min/avg/max 0.001/5.724/283.186).
	5 slowest boards: showstopper_9 (283.2s), grande_10 (173.9s), diagonal_10 (146.6s), showstopper_10 (67.1s), grande_9 (27.5s)
    ```
