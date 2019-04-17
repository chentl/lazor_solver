Last update: April 17, 2019 13:00

***** This readme file will be used as 'project status' unitl the code is complete and robust *****

# lazor_solver
module to solve for board puzzles of the "Lazors" game in Android and iOS

Underdevelopment:
  - Image loader of board to solve
  the initial image processessing can yield the following, wondering if Template Matching can work here?
  
  <img src="/utilites/img_reader/Mad_7.jpg" alt="drawing" width="200"/> ---> <img src="/utilites/img_reader/Result_IMAGE.png" alt="drawing" width="200"/>
  
  
  <img src="/utilites/img_reader/Diagonal_3.jpg" alt="drawing" width="200"/> ---> <img src="/utilites/img_reader/Result_IMAGE_Diagonal_3.png" alt="drawing" width="200"/>

    

The loader and solver are running smoothly, however there are multiple issues that can be addressed and solved:
  - the function *get_possible_combs_perm* returns more than needed combinations, this can be due to sorting issues
  - possibly after commiting the image loader, merge with the bff_loader to take input as either bff file or image

Finally, we need to wrap all functions into a class once the missing functinos are added.

## Changes in `dev` branch

- refactor `solve.py` and other module files inside `pylazors`.
- add a `_solver.py` which contains functions used to solve large boards.
- add a wrapper function in `solve.py`, `solve_board()`. This function will check the size of the given board, 
  if it is small, use `_solve_board()` in `solve.py`, and if it is large, use `_solve_large_board()` in `_solve.py`.
- add a small main script `lazors.py`
- add error handling

## Todos
- Error handing
- Unit testing
- Add back docstrings in original main script (project description, file information, etc)

## Performance

for boards in `boards/handout`:

```
[solve_all] 8 boards solved in 11.155 seconds (min/avg/max 0.001/1.394/6.208).
[solve_all] 5 slowest boards: yarn_5 (6.2s), mad_7 (4.5s), numbered_6 (0.2s), mad_4 (0.1s), mad_1 (0.1s)
```

for boards in `boards/all`:

```
[solve_all] 157 boards solved in 732.311 seconds (min/avg/max 0.000/4.664/250.364).
[solve_all] 5 slowest boards: showstopper_9 (250.4s), grande_10 (142.1s), diagonal_10 (117.9s), showstopper_10 (69.3s), grande_9 (22.1s)
```