import pylazors
import glob
import os
import time
from multiprocessing import Pool
from functools import partial


board_dir = 'boards'
solution_dir = 'solutions'


def solve_one(board, verbose=True):
    """ Solve one of board, print solution, and return solution board and timing info.
    Set *verbose* to False to disable detail logging inside pylazors.solve_board.
    """

    if verbose:
        print('')
    print('[solve_one] %s: start solving' % str(board))

    start_time = time.time()
    solution_board = pylazors.solve_board(board, print_log=verbose)
    time_used = time.time() - start_time

    if solution_board is not None:
        img_name = os.path.join(solution_dir, solution_board.name + '.png')
        note = 'solved in %.3f seconds' % time_used
        pylazors.write_png(solution_board, img_name, note)
        print('[solve_one] %s: solution found in %f seconds, saved to %s.' % (str(board), time_used, img_name))
    else:
        print('[solve_one] %s: No solution found after testing all possible combinations, time used: %f seconds' %
              (str(board), time_used))
    return solution_board, time_used


def solve_all(boards, processes=1):
    """ Solve a list of boards, print timing information, and return solution boards.

     *processes* controls how many processes will be used to solve boards in parallel, set this to 0 will set
     the number of processes to half of available cpu counts.

     Note: when *processes* > 1, the returned *solution_board* list may not have the same order as the input
     *boards* list, because this function will try to solve largest board first in order to maximized performance.
    """

    if processes == 0:
        processes = os.cpu_count() // 2

    if processes == 1:
        verbose = True
    else:
        verbose = False
        boards.sort(key=lambda b: b.get_estimate_complexity(), reverse=True)
    print('\n[solve_all] Using %d process(es).' % processes)
    print('[solve_all] List of boards:', ', '.join([b.name for b in boards]))
    pool = Pool(processes)
    start_time = time.time()
    results = pool.map(partial(solve_one, verbose=verbose), boards, chunksize=1)

    print('\n' + '=' * 80)

    print('[solve_all] All jobs done. %d boards solved. Total wall time: %.2f seconds' % (
        len(boards), time.time() - start_time))

    solutions = [r[0] for r in results]
    time_history = [(r[0].name, r[1]) for r in results]
    t_list = [x[1] for x in time_history]
    t_sum, t_min, t_max = sum(t_list), min(t_list), max(t_list)

    print('[solve_all] Total CPU time: %.3f seconds (min/avg/max %.3f/%.3f/%.3f).' % (
        t_sum, t_min, t_sum / len(boards), t_max))
    if len(boards) > 5:
        top_5 = list(reversed(sorted(time_history, key=lambda x: x[1])))[:5]
        print('[solve_all] 5 slowest boards: ' + ', '.join(['%s (%.1fs)' % h for h in top_5]))
    print('=' * 80 + '\n')

    return solutions


def load_dir(dir_name):
    """ Load all BFF file inside *dir_name* """

    skipped = 0
    all_boards = []
    for bff_file in sorted(glob.glob(os.path.join(board_dir, dir_name, '*.bff'))):
        try:
            all_boards.append(pylazors.read_bff(bff_file))
            print('[load_dir] load board:', all_boards[-1])
        except pylazors.BFFReaderError as e:
            skipped += 1
            print('[load_dir] Skip loading due to error:', e)
    print('[load_dir] %d boards loaded from "%s".' % (len(all_boards), dir_name))
    if skipped:
        print('[load_dir] %d boards skipped because of error from "%s".' % (skipped, dir_name))
    return all_boards


if __name__ == '__main__':
    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)

    # Solve all boards given in the handout, running in serial.
    solve_all(load_dir('handout'))

    # Solve all boards in the game, running in parallel.
    solve_all(load_dir('all'), processes=0)
