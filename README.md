Last update: April 6, 2019 21:00

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

## Todos in `dev` branch
- Error handing
- Unit testing
- Add back docstrings in original main script (project description, file information, etc)